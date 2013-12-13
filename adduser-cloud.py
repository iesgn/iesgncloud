#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from getpass import getpass
import ldap
import ConfigParser
from keystoneclient.v2_0 import client as keystonec
from quantumclient.quantum import client as quantumc
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
    
# LDAP parameters read from config file
config = ConfigParser.ConfigParser()
config.read("adduser-cloud.conf")
    
# LDAP binding
path = config.get("ldap", "path")
l = ldap.open(config.get("ldap", "ldap_server"))

while True:
    ldap_user_rdn = raw_input("LDAP admin rdn value (tipically username): ")
    bind_user = "%s=%s,%s" % (config.get("ldap","user_rdn_attrib"),
                              ldap_user_rdn,
                              path)
    bind_pass = getpass("LDAP admin password: ")
    try:
        l.simple_bind_s(bind_user, bind_pass)
        break
    except ldap.INVALID_CREDENTIALS:
        print "Invalid LDAP username or password"

# 3 attributes are defined into a list:
# - rdn attribute (usually cn or uid)
# - mail
# - LDAP attrib containing password (SHA512 hash with salt)
attrib_list = [config.get("ldap","user_rdn_attrib"),
               'mail',
               config.get("ldap","user_pass_attrib")]
# LDAP Filter (inetOrgPerson with attributes defined in attrib_list
ldapfilter = '(&(objectClass=inetOrgPerson)(%s=*)(%s=%s))' % (attrib_list[2],
                                                              attrib_list[0],
                                                              user)

ldap_users = l.search_s(path, ldap.SCOPE_SUBTREE, ldapfilter, attrib_list)

if len(ldap_users) == 0:
    print "User(s) not found in LDAP tree"
    sys.exit()
    
# Getting auth token from keystone
creds = get_keystone_creds()
try:
    keystone = ksclient.Client(**creds)
except keystonec.exceptions.Unauthorized:
    print "Invalid keystone username or password"
    sys.exit()

admintoken = keystone.auth_token

# Defining member role id
for role in keystone.roles.list():
    if role.name == '_member_':
        member_role_id = role.id

for member in ldap_users:
    username = member[1]["%s" % attrib_list[0]][0]
    # If user exists in keystone, user password is updated
    for oldmember in keystone.users.list():
        if oldmember.name == username:
            new_passwd = member[1]["%s" % lista_atrib[2]][0]
            keystone.users.update_password(oldmember.id,new_passwd)
            sys.exit(0)

    # If user does not exist:
    # - user is created
    # - proy-username tenant is created
    # - member role is assigned to user in tenant proy-username
    # - a network is created in tenant proy-username
    # - a subnet 10.0.0.0/24 is defined in newnetwork
    # - a router is created in tenant proy-username
    # - router gateway is defined in a external network previously created
    # - router interface is created in subnet 10.0.0.0/24
    newmember = keystone.users.create(username,
                                      member[1]["%s" % attrib_list[2]][0],
                                      member[1]["%s" % attrib_list[1]][0])
    print "Creating new user with id %s" % newmember.id
    newtenant = keystone.tenants.create("proy-%s" % username,
                                        "proyecto de %s" % username)
    print "Creating new tenant with id %s" % newtenant.id
    keystone.roles.add_user_role(newmember.id,
                                 member_role_id,
                                 newtenant.id)
    quantum = quantumc.Client('2.0',
                              endpoint_url=config.get("quantum","endpoint"),
                              token = keystone.auth_token)
    quantum.format = 'json'
    network = {'name':'red interna de %s' % username,
               'tenant_id': newtenant.id,
               'admin_state_up': True}
    newnetwork = quantum.create_network({'network':network})
    print "Creating new network with id %s" % newnetwork['network']['id']
    subnet = {'network_id': newnetwork['network']['id'],
              'ip_version':4,
              'cidr':'10.0.0.0/24',
              'enable_dhcp': True,
              'tenant_id': newtenant.id,
              'dns_nameservers': ['%s' % config.get("quantum","dns_nameservers")]}
    newsubnet = quantum.create_subnet({'subnet':subnet})
    print "Creating new subnet with id %s" % newsubnet['subnet']['id']
    router = {'name':'router de %s' % username,
              'tenant_id': newtenant.id,
              'external_gateway_info':{'network_id':
                                       config.get("quantum","external_net_id")},
              'admin_state_up': True}
    newrouter = quantum.create_router({'router':router})
    print "Creating new router with id %s" % newrouter['router']['id']
    quantum.add_interface_router(newrouter['router']['id'],
                                 {'subnet_id': newsubnet['subnet']['id']})
    print "Connecting router to subnet %s" % newsubnet['subnet']['id']
    sys.exit(0)
    