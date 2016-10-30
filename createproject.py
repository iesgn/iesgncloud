#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Python script used to create projects and a network for every OpenStack
User from an LDAP directory. It requires previous LDAP configuration
in keystone
"""
import sys
import ConfigParser
import requests
from keystoneclient.v3 import client as keystonec
from neutronclient.neutron import client as neutronc
from credentials import get_keystone_v3_creds

if len(sys.argv) == 2:
    user = sys.argv[1]
    print "Adding user %s to OpenStack" % user
else:
    print """
    If you want to create or modify ONLY ONE USER, please use:
    $ adduser-cloud <username>
    """
    if raw_input("Are you sure you want to continue (y/n)? ") != 'y':
        sys.exit()
    user = "*"
    print "Adding or modifying ALL users"
    
config = ConfigParser.ConfigParser()
config.read("adduser-cloud.conf")
    
    
# Getting auth token from keystone
try:
    creds = get_keystone_v3_creds()
    keystone = keystonec.Client(**creds)
except keystonec.exceptions.Unauthorized:
    print "Invalid keystone username or password"
    sys.exit()

# Getting domain
try:
    domain = keystone.domains.find(
        name=config.get("keystone","domain"))
except keystonec.exceptions.NotFound:
    print "Domain not found"
    sys.exit()
    
user_list = keystone.users.list(domain = domain)
    
# For every user in list a new project is created
for member in user_list:
    # If user's project exists in keystone, user is ignored
    try:
        keystone.projects.find(name="Proyecto de %s" % member.name)
        continue
    except keystonec.exceptions.NotFound:
        print "Creating new project for user %s" % member.name

    # If user's project doesn't exist previously:
    # - "Proyecto de <username>" project is created
    # - user role is aggined to user in the project
    # - a network with name "red de <username>" is created in the project
    # - a subnet 10.0.0.0/24 is defined in the network
    # - a router is created in the project
    # - router gateway is defined in a external network previously created
    # - router interface is created in subnet 10.0.0.0/24

    # Creating new project
    defaultDomain = keystone.domains.find(name="default")
    project = keystone.projects.create(name = "Proyecto de %s" % member.name,
                                       domain = defaultDomain,
                                       description = "Proyecto de %s" % member.name)
    print "Creating new project with id %s" % project.id
    # Assigning selected role to member in the project with python requests
    headers = {"X-Auth-Token":keystone.auth_token,
               "Content-Type": "application/json"}
    user_role = keystone.roles.find(name=config.get("keystone","role"))
    url = "%s/projects/%s/users/%s/roles/%s" % (config.get("keystone","url"),
                                                project.id,
                                                member.id,
                                                user_role.id)
    try:
        requests.put(url,headers=headers)
        print "Assigning user role"
    except requests.exceptions.RequestException as e:
        print e
        sys.exit(1)
        
    neutron = neutronc.Client('2.0',
                              endpoint_url=config.get("neutron","endpoint"),
                              token = keystone.auth_token)
    neutron.format = 'json'
    network = {'name':'red de %s' % member.name,
               'project_id': project.id,
               'admin_state_up': True}
    newnetwork = neutron.create_network({'network':network})
    print "Creating new network with id %s" % newnetwork['network']['id']
    subnet = {'network_id': newnetwork['network']['id'],
              'ip_version':4,
              'cidr':'10.0.0.0/24',
              'enable_dhcp': True,
#              'tenant_id': project.id,
              'dns_nameservers': ['%s' % config.get("neutron","dns_nameservers")]}
    newsubnet = neutron.create_subnet({'subnet':subnet})
    print "Creating new subnet with id %s" % newsubnet['subnet']['id']
    router = {'name':'router de %s' % username,
              'project_id': project.id,
              'external_gateway_info':{'network_id':
                                       config.get("neutron","external_net_id")},
              'admin_state_up': True}
    newrouter = neutron.create_router({'router':router})
    print "Creating new router with id %s" % newrouter['router']['id']
    neutron.add_interface_router(newrouter['router']['id'],
                                 {'subnet_id': newsubnet['subnet']['id']})
    print "Connecting router to subnet %s" % newsubnet['subnet']['id']
    
