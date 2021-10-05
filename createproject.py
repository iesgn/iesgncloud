#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Python script used to create projects and a network for every OpenStack
User from an LDAP directory. It requires previous LDAP configuration
in keystone
"""
import sys
import configparser
from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client as keystonec
from neutronclient.v2_0 import client as neutronc
from credentials import get_keystone_v3_creds

def helpUsage():
    print ("""
    If you want to create projects for ALL users in domain:
    createproject

    If you want to create a project for one user in domain:
    createproject <username>
    """)

config = configparser.ConfigParser()
config.read("adduser-cloud.conf")
domainname = config.get("default","domain")

if len(sys.argv) == 2:
    user = sys.argv[1]
    print ("Adding project for user %s in domain %s" % (user,domainname))
else:
    print ("You're going to create projects for all the users in domain %s" % domainname)
    if input("Are you sure you want to continue (y/n)? ") != 'y':
        helpUsage()
        sys.exit(1)
    user = "*"
    print ("Adding or modifying projects for ALL the users")

# Getting auth token from keystone with a session
try:
    creds = get_keystone_v3_creds()
    auth = v3.Password(**creds)
    sess = session.Session(auth=auth)
    keystone = keystonec.Client(session=sess)
except keystonec.exceptions.Unauthorized:
    print ("Invalid keystone username or password")
    sys.exit(1)

# Getting domain
try:
    domain = keystone.domains.find(name = domainname)
except keystonec.exceptions.NotFound:
    print ("Domain not found")
    sys.exit(1)

if user == '*':
    user_list = keystone.users.list(domain = domain)
else:
    user_list = [keystone.users.find(name = user,
                                     domain = domain)]

# For every user in list a new project is created
for member in user_list:
    # If user's project exists in keystone, user is ignored
    try:
        keystone.projects.find(name="Proyecto de %s" % member.name)
        continue
    except keystonec.exceptions.NotFound:
        print ("Creating a new project for user %s" % member.name)

    # If user's project doesn't exist previously:
    # - "Proyecto de <username>" project is created
    # - member role is asiggned to the user in the project
    # - heat_stack_owner role is assigned to the user in the project
    # - a network with name "red de <username>" is created in the project
    # - a subnet 10.0.0.0/24 is defined in the network
    # - a router is created in the project
    # - router gateway is defined in a external network previously created
    # - router interface is created in subnet 10.0.0.0/24

    # Creating a new project
    project = keystone.projects.create(name = "Proyecto de %s" % member.name,
                                       domain = domain,
                                       description = "Proyecto de %s" % member.name)
    print ("Creating new project with id %s" % project.id)

    # Assigning roles to the user
    roles_to_add = ['member',
                    'swiftoperator',
                    'load-balancer_member',
                    'heat_stack_owner']

    for role_to_add in roles_to_add:
        role = keystone.roles.find(name = role_to_add)
        keystone.roles.grant(role = role,
                             user = member,
                             project = project)
        print ("Role %s assigned to user in project" % role_to_add)

    neutron = neutronc.Client(session=sess,endpoint_type='internalURL')
    network = {'name':'red de %s' % member.name,
               'project_id': project.id,
               'admin_state_up': True}
    newnetwork = neutron.create_network({'network':network})
    print ("Creating new network with id %s" % newnetwork['network']['id'])
    subnet = {'network_id': newnetwork['network']['id'],
              'ip_version':4,
              'cidr':'10.0.0.0/24',
              'enable_dhcp': True,
              'project_id': project.id,
              'dns_nameservers': ['%s' % config.get("default","dns_nameserver")]}
    newsubnet = neutron.create_subnet({'subnet':subnet})
    print ("Creating new subnet with id %s" % newsubnet['subnet']['id'])
    router = {'name':'router de %s' % member.name,
              'project_id': project.id,
              'external_gateway_info':{'network_id':
                                       config.get("default","external_net_id")},
              'admin_state_up': True}
    newrouter = neutron.create_router({'router':router})
    print ("Creating new router with id %s" % newrouter['router']['id'])
    neutron.add_interface_router(newrouter['router']['id'],
                                 {'subnet_id': newsubnet['subnet']['id']})
    print ("Connecting router to subnet %s" % newsubnet['subnet']['id'])

sys.exit(0)
