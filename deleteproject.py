#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Python script used to delete a project from a domain, including the deletion
of the project's objects: instances, volumes, floating IPs, etc.
"""
import sys
import ConfigParser
import requests
from keystoneclient.v3 import client as keystonec
# from novaclient.v2 import client as novac
# from cinderclient.v2 import client as cinderc
# from neutronclient.v2_0 import client as neutronc
# from glanceclient.v2 import client as glancec
from credentials import get_keystone_v3_creds

if len(sys.argv) == 2:
    project = sys.argv[1]
    print "Deleting project %s and all its related objects" % project
else:
    print """
    Usage: 
    deleteproject <project_id>
    """
    sys.exit()
    
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

catalog = keystone.endpoints.list()

nova_endpoint = next(( endpoint for endpoint in catalog
                       if endpoint.service_id == "compute"
                       and endpoint.interface == "admin"), None)
nova_endpoint.url = nova_endpoint.url.replace("$(tenant_id)",
                                              keystone.project_id)
neutron_endpoint = next(( endpoint for endpoint in catalog
                          if endpoint.service_id == "network"
                          and endpoint.interface == "admin"), None)
cinder_endpoint = next(( endpoint for endpoint in catalog
                         if endpoint.service_id == "volumev2"
                         and endpoint.interface == "admin"), None)
cinder_endpoint.url = cinder_endpoint.url.replace("$(tenant_id)s",
                                                  keystone.project_id)
glance_endpoint = next(( endpoint for endpoint in catalog
                          if endpoint.service_id == "image"
                          and endpoint.interface == "admin"), None)

    
