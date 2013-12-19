#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from quantumclient.v2_0 import client as quantumc
from keystoneclient.v2_0 import client as keystonec
from credentials import get_keystone_creds

if len(sys.argv) == 2:
    tenant_name = sys.argv[1]
    print "Deleting routers from tenant %s " % tenant_name
else:
    print "You must provide tenant_name"
    sys.exit()

# Getting auth token from keystone
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
    
for router in quantum.list_routers(tenant_id=tenant.id)["routers"]:
    quantum.remove_gateway_router(router["id"])
    for port in quantum.list_ports(tenant_id=tenant.id)["ports"]:
        if port["device_id"] == router["id"]:
            quantum.remove_interface_router(router["id"],{'port_id':port["id"]})
            quantum.delete_router(router["id"])
            break

