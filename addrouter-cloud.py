#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import ConfigParser
from quantumclient.quantum import client as quantumc
from keystoneclient.v2_0 import client as keystonec
from credentials import get_keystone_creds

if len(sys.argv) == 3:
    tenant_name = sys.argv[1]
    ext_net = sys.argv[2]
    print "Creating routers for every subnet of tenant %s " % tenant_name
else:
    print "You must provide tenant_name and external network name"
    sys.exit()

config = ConfigParser.ConfigParser()
config.read("adduser-cloud.conf")

try:
    creds = get_keystone_creds()
    keystone = keystonec.Client(**creds)
except keystonec.exceptions.Unauthorized:
    print "Invalid keystone username or password"
    sys.exit()

quantum = quantumc.Client('2.0',
                          endpoint_url=config.get("quantum","endpoint"),
                          token = keystone.auth_token)
   
tenant = keystone.tenants.find(name=tenant_name)
username = tenant.name.split("-")[1]
for net in quantum.list_networks()["networks"]:
    if net["name"] == ext_net and net['router:external'] == True:
        external_net = net
        break

# Create a router connected to external network for every subnet
for subnet in quantum.list_subnets(tenant_id=tenant.id)["subnets"]:
    router = {'name':'router de %s' % username,
              'tenant_id': tenant.id,
              'external_gateway_info':{'network_id':external_net["id"]},
              'admin_state_up': True}
    newrouter = quantum.create_router({'router':router})
    print "Creating new router with id %s" % newrouter['router']['id']
    quantum.add_interface_router(newrouter['router']['id'],
                                 {'subnet_id': subnet['id']})
    print "Connecting router to subnet %s" % subnet['id']
    
