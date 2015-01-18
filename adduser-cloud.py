#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import ldap
import ConfigParser
from keystoneclient.v2_0 import client as keystonec
from neutronclient.neutron import client as neutronc
from credentials import get_keystone_creds

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
    
# LDAP binding
ldap_bind_dn = config.get("ldap", "ldap_bind_dn")
ldap_bind_pass = config.get("ldap", "ldap_bind_pass")
l = ldap.open(config.get("ldap", "ldap_server"))
try:
    l.simple_bind_s(ldap_bind_dn, ldap_bind_pass)
except ldap.INVALID_CREDENTIALS:
    print "Invalid LDAP bind user dn or password"
    sys.exit(0)

# 3 attributes are defined into a list:
# - rdn attribute (usually cn or uid)
# - mail
# - Additional attribute for filtering
user_attrib = config.get("ldap","user_rdn_attrib")
mail_attrib = config.get("ldap","user_mail_attrib")
additional_attrib = config.get("ldap","user_additional_attrib")
additional_value = config.get("ldap","user_additional_value")
path = config.get("ldap","ldap_base")
# LDAP Filter (inetOrgPerson with attributes defined in attrib_list
ldapfilter = '(&(objectClass=inetOrgPerson)(%s=%s)(%s=%s))' % (user_attrib,
                                                               user,
                                                               additional_attrib,
                                                               additional_value)

ldap_users = l.search_s(path, ldap.SCOPE_SUBTREE, ldapfilter, (user_attrib,
                                                               mail_attrib))

if len(ldap_users) == 0:
    print "User(s) not found in LDAP tree"
    sys.exit()
    
# Getting auth token from keystone
try:
    creds = get_keystone_creds()
    keystone = keystonec.Client(**creds)
except keystonec.exceptions.Unauthorized:
    print "Invalid keystone username or password"
    sys.exit()

# For every user in ldap search, a keystone user is created or password is updated
for member in ldap_users:
    username = member[1]["%s" % user_attrib][0]
    # If user exists in keystone, user password is updated
    try:
        oldmember = keystone.users.find(name=username)
        if raw_input("Modify user password for %s (y/N)? " % username) == 'y':
            new_passwd = config.get("default","password")
            keystone.users.update_password(oldmember.id,new_passwd)
            print "Password for %s updated" % oldmember.name
        continue
    except keystonec.exceptions.NotFound:
        print "Creating new user %s" % username

    # If user does not exist:
    # - "Proyecto de <username>" tenant is created
    # - user is created with member role in tenant
    # - a network is created in tenant Proyecto de username
    # - a subnet 10.0.0.0/24 is defined in newnetwork
    # - a router is created in tenant Proyecto de username
    # - router gateway is defined in a external network previously created
    # - router interface is created in subnet 10.0.0.0/24
    newtenant = keystone.tenants.create("Proyecto de %s" % username,
                                        "Proyecto de %s" % username)
    print "Creating new tenant with id %s" % newtenant.id
    newmember = keystone.users.create(username,
                                      password=config.get("default","password"),
                                      email=member[1]["%s" % mail_attrib][0],
                                      tenant_id=newtenant.id)
    print "Creating new user with id %s" % newmember.id
    neutron = neutronc.Client('2.0',
                              endpoint_url=config.get("neutron","endpoint"),
                              token = keystone.auth_token)
    neutron.format = 'json'
    network = {'name':'red de %s' % username,
               'tenant_id': newtenant.id,
               'admin_state_up': True}
    newnetwork = neutron.create_network({'network':network})
    print "Creating new network with id %s" % newnetwork['network']['id']
    subnet = {'network_id': newnetwork['network']['id'],
              'ip_version':4,
              'cidr':'10.0.0.0/24',
              'enable_dhcp': True,
              'tenant_id': newtenant.id,
              'dns_nameservers': ['%s' % config.get("neutron","dns_nameservers")]}
    newsubnet = neutron.create_subnet({'subnet':subnet})
    print "Creating new subnet with id %s" % newsubnet['subnet']['id']
    router = {'name':'router de %s' % username,
              'tenant_id': newtenant.id,
              'external_gateway_info':{'network_id':
                                       config.get("neutron","external_net_id")},
              'admin_state_up': True}
    newrouter = neutron.create_router({'router':router})
    print "Creating new router with id %s" % newrouter['router']['id']
    neutron.add_interface_router(newrouter['router']['id'],
                                 {'subnet_id': newsubnet['subnet']['id']})
    print "Connecting router to subnet %s" % newsubnet['subnet']['id']
    
