#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Python script used to delete a project from a domain, including the deletion
of the following objects: 
 * instances
 * volume snapshots
 * volumes
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
import json

if len(sys.argv) == 2:
    project = sys.argv[1]
    print "Deleting project %s and all its related objects" % project_id
else:
    print """
    Usage: 
    deleteproject <project_id>
    """
    sys.exit()
    
config = ConfigParser.ConfigParser()
config.read("adduser-cloud.conf")

# Getting auth token from keystonetry:
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

neutron_endpoint = next(( endpoint for endpoint in catalog
                          if endpoint.service_id == "network"
                          and endpoint.interface == "public"), None)
glance_endpoint = next(( endpoint for endpoint in catalog
                          if endpoint.service_id == "image"
                          and endpoint.interface == "public"), None)

nova_endpoint = next(( endpoint for endpoint in catalog
                       if endpoint.service_id == "compute"
                       and endpoint.interface == "public"), None)
nova_endpoint.url = nova_endpoint.url.replace("$(tenant_id)s",
                                              keystone.project_id)

headers = {"X-Auth-Token":keystone.auth_token,
           "Content-Type": "application/json"}

# Get all servers and store them in a JSON object

try:
    servers = requests.get("%s/servers/detail" % nova_endpoint.url,
                           headers=headers,
                           params={"all_tenants":True})
    if servers.status_code == 200:
        servers_json = json.loads(servers.text)

except requests.exceptions.RequestException as e:
    print e
    sys.exit(1)

# Delete all servers beloging to project project_id

for server in servers_json["servers"]:
    if server["tenant_id"] == project_id:
        try:
            r = requests.delete("%s/servers/%s" % (nova_endpoint.url,
                                                   server["id"]),
                                headers=headers)
            if r.status_code == 202:
                print "Request to delete server %s has been accepted." % server["id"]
        except requests.exceptions.RequestException as e:
            print e
            sys.exit(1)

# Get Cinder public endpoint

cinder_endpoint = next(( endpoint for endpoint in catalog
                         if endpoint.service_id == "volumev2"
                         and endpoint.interface == "public"), None)
cinder_endpoint.url = cinder_endpoint.url.replace("$(tenant_id)s",
                                                  keystone.project_id)

# Get all snapshots and store then in a JSON object

try:
    snapshots = requests.get("%s/snapshots/detail" % cinder_endpoint.url,
                             headers=headers,
                             params={"all_tenants":True})
    if snapshots.status_code == 200:
        snapshots_json = json.loads(snapshots.text)
        
except requests.exceptions.RequestException as e:
    print e
    sys.exit(1)
    
for snapshot in snapshots_json["snapshots"]:
    if snapshot["tenant_id"] == project_id:
        try:
            r = requests.delete("%s/snapshots/%s" % (cinder_endpoint.url,
                                                 snapshot["id"]),
                            headers=headers)
            if r.status_code == 202:
                print "Request to delete snapshot %s has been accepted." % snapshot["id"]
        except requests.exceptions.RequestException as e:
            print e
            sys.exit(1)

try:
    volumes = requests.get("%s/volumes/detail" % cinder_endpoint.url,
                           headers=headers,
                           params={"all_tenants":True})
    if volumes.status_code == 200:
        volumes_json = json.loads(volumes.text)
        
except requests.exceptions.RequestException as e:
    print e
    sys.exit(1)
    
for volume in volumes_json["volumes"]:
    if volume["os-vol-tenant-attr:tenant_id"] == project_id and volume["status"] != "in-use":
        try:
            r = requests.delete("%s/volumes/%s" % (cinder_endpoint.url,
                                                   volume["id"]),
                                headers=headers)
            if r.status_code == 202:
                print "Request to delete volume %s has been accepted." % volume["id"]
        except requests.exceptions.RequestException as e:
            print e
            sys.exit(1)

