#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Python script used to delete a project from a domain, including the deletion
of the following objects: 
 * instances
 * volume snapshots
 * volumes
 * floating IPs
 * security groups
"""
import sys
import ConfigParser
import requests
from keystoneclient.v3 import client as keystonec
from keystoneclient.auth.identity import v3
from keystoneclient import session
#from novaclient.v2 import client as novac
# from cinderclient.v2 import client as cinderc
from neutronclient.v2_0 import client as neutronc
from glanceclient.v2 import client as glancec
from credentials import get_keystone_v3_creds
import json
import time

if len(sys.argv) == 2:
    project_id = sys.argv[1]
    print "Deleting project %s and all its related objects" % project_id
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

# Verifying admin role for user
try:
    keystone.users.list()
except keystonec.exceptions.Forbidden:
    print "You are not authorized to execute this pregram, admin role needed"
    sys.exit()
    
# Getting domain
# try:
#     domain = keystone.domains.find(
#         name=config.get("keystone","domain"))
# except keystonec.exceptions.NotFound:
#     print "Domain not found"
#     sys.exit()

catalog = keystone.endpoints.list()

headers = {"X-Auth-Token":keystone.auth_token,
           "Content-Type": "application/json"}

# Nova: Deleting all servers

nova_endpoint = next(( endpoint for endpoint in catalog
                       if endpoint.service_id == "compute"
                       and endpoint.interface == "public"), None)

nova_endpoint.url = nova_endpoint.url.replace("$(tenant_id)s",
                                              keystone.project_id)


try:
    servers = requests.get("%s/servers/detail" % nova_endpoint.url,
                           headers=headers,
                           params={
                               "all_tenants":True,
                               "project_id":project_id
                               })
    if servers.status_code == 200:
        servers_json = json.loads(servers.text)

except requests.exceptions.RequestException as e:
    print e
    sys.exit(1)

for server in servers_json["servers"]:
    try:
        r = requests.delete("%s/servers/%s" % (nova_endpoint.url,
                                               server["id"]),
                            headers=headers)
        if r.status_code == 202:
            print "Request to delete server %s has been accepted." % server["id"]
    except requests.exceptions.RequestException as e:
        print e
        sys.exit(1)

# Cinder: Deleting snapshots and volumes

cinder_endpoint = next(( endpoint for endpoint in catalog
                         if endpoint.service_id == "volumev2"
                         and endpoint.interface == "public"), None)
cinder_endpoint.url = cinder_endpoint.url.replace("$(tenant_id)s",
                                                  keystone.project_id)

try:
    snapshots = requests.get("%s/snapshots/detail" % cinder_endpoint.url,
                             headers=headers,
                             params={
                                 "all_tenants":True,
                                 "project_id":project_id
                             })
    if snapshots.status_code == 200:
        snapshots_json = json.loads(snapshots.text)
        
except requests.exceptions.RequestException as e:
    print e
    sys.exit(1)

for snapshot in snapshots_json["snapshots"]:
    try:
        r = requests.delete("%s/snapshots/%s" % (cinder_endpoint.url,
                                                 snapshot["id"]),
                            headers=headers)
        if r.status_code == 202:
            print "Request to delete snapshot %s has been accepted." % snapshot["id"]
    except requests.exceptions.RequestException as e:
        print e
        sys.exit(1)

# Waiting until there were no snapshots available, because a volume can't be deleted
# while any associated snapshot exists

while True:
    snapshots = requests.get("%s/snapshots/detail" % cinder_endpoint.url,
                             headers=headers,
                             params={
                                 "all_tenants":True,
                                 "project_id":project_id
                             })
    if len(json.loads(snapshots.text)["snapshots"]) == 0:
        break
    else:
        print "Waiting until associated snapshots are deleted ..."
        time.sleep(5)

try:
    volumes = requests.get("%s/volumes/detail" % cinder_endpoint.url,
                           headers=headers,
                           params={
                               "all_tenants":True,
                               "project_id":project_id
                           })
    if volumes.status_code == 200:
        volumes_json = json.loads(volumes.text)
        
except requests.exceptions.RequestException as e:
    print e
    sys.exit(1)
    
for volume in volumes_json["volumes"]:
    try:
        r = requests.delete("%s/volumes/%s" % (cinder_endpoint.url,
                                               volume["id"]),headers=headers)
        if r.status_code == 202:
            print "Request to delete volume %s has been accepted." % volume["id"]
    except requests.exceptions.RequestException as e:
        print e
        sys.exit(1)

# Neutron: Deleting routers, subnets, networks, security groups and releasing floating IPs

# Using keystone session because Neutron hasn't Keystone V3 support

auth = v3.Password(**creds)
sess = session.Session(auth=auth)
neutron = neutronc.Client(session=sess)

# Deleting all security groups but default

for sec_group in neutron.list_security_groups()['security_groups']:
    if sec_group['project_id'] == project_id and sec_group['name'] != "default":
        neutron.delete_security_group(sec_group['id'])
        print "Security group %s deleted" % sec_group['id']

# Deleting floating IPs

for ip in neutron.list_floatingips()['floatingips']:
    if ip['project_id'] == project_id:
        neutron.delete_floatingip(ip['id'])
        print "Floating IP %s released" % ip['floating_ip_address']

# Deleting routers

for router in neutron.list_routers()['routers']:
    if router['project_id'] == project_id:
        neutron.remove_gateway_router(router['id'])
        for port in neutron.list_ports(project_id=project_id)["ports"]:
            if port["device_id"] == router["id"]:
                neutron.remove_interface_router(router["id"],{'port_id':port["id"]})
        if router['project_id'] == project_id:
            neutron.delete_router(router['id'])
            print "%s deleted" % router['name']

# Deleting subnetworks

for subnet in neutron.list_subnets()['subnets']:
    if subnet['project_id'] == project_id:
        neutron.delete_subnet(subnet['id'])
        print "Subnetwork %s deleted" % subnet['id']

# Deleting networks

for network in neutron.list_networks()['networks']:
    if network['project_id'] == project_id:
        neutron.delete_network(network['id'])
        print "%s deleted" % network['name']
                        
# Glance: Deleting images

glance = glancec.Client(session=sess)

for image in glance.images.list():
    if image["owner"] == project_id:
        glance.images.delete(image["id"])
        print "Image %s deleted" % image["name"]                             


