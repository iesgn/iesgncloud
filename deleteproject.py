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
from novaclient.v2 import client as novac
# from cinderclient.v2 import client as cinderc
# from neutronclient.v2_0 import client as neutronc
# from glanceclient.v2 import client as glancec
from credentials import get_keystone_v3_creds
import json

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
                           params={"all_tenants":True})
    if servers.status_code == 200:
        servers_json = json.loads(servers.text)

except requests.exceptions.RequestException as e:
    print e
    sys.exit(1)

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

# Cinder: Deleting snapshots and volumes

cinder_endpoint = next(( endpoint for endpoint in catalog
                         if endpoint.service_id == "volumev2"
                         and endpoint.interface == "public"), None)
cinder_endpoint.url = cinder_endpoint.url.replace("$(tenant_id)s",
                                                  keystone.project_id)

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
    if snapshot["os-extended-snapshot-attributes:project_id"] == project_id:
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
    if volume["os-vol-tenant-attr:tenant_id"] == project_id:
        try:
            r = requests.delete("%s/volumes/%s" % (cinder_endpoint.url,
                                                   volume["id"]),
                                headers=headers)
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

# Deleting security groups

for sec_group in neutron.list_security_groups()['security_groups']:
    if sec_group['tenant_id'] == project_id:
        neutron.delete_security_group(sec_group['id'])
        print "Deleted security group %s" % sec_group['id']

# Deleting floating IPs

for ip in neutron.list_floatingips()['floatingips']:
    if ip['tenant_id'] == project_id:
        neutron.delete_floatingip(ip['id'])
        print "Deleted floating IP %s" % ip['id']

# Deleting routers

for router in neutron.list_routers()['routers']:
    if router['tenant_id'] == project_id:
        neutron.remove_gateway_router(router['id'])
        for port in neutron.list_ports(tenant_id=project_id)["ports"]:
            if port["device_id"] == router["id"]:
                neutron.remove_interface_router(router["id"],{'port_id':port["id"]})
        if router['tenant_id'] == project_id:
            neutron.delete_router(router['id'])
            print "Deleted router %s" % router['id']

# Deleting subnetworks

for subnet in neutron.list_subnets()['subnets']:
    if subnet['tenant_id'] == tenant_id:
        neutron.delete_subnet(subnet['id'])
        print "Deleted subnetwork %s" % subnet['id']

# Deleting networks

for network in neutron.list_networks()['networks']:
    if network['tenant_id'] == tenant_id:
        neutron.delete_network(network['id'])
        print "Deleted network %s" % network['id']
                        
# neutron_endpoint = next(( endpoint for endpoint in catalog
#                           if endpoint.service_id == "network"
#                           and endpoint.interface == "public"), None)

# try:
#     floating_ips = requests.get("%s/v2.0/floatingips" % neutron_endpoint.url,
#                                 headers=headers)
#     if floating_ips.status_code == 200:
#         floating_ips_json = json.loads(floating_ips.text)
        
# except requests.exceptions.RequestException as e:
#     print e
#     sys.exit(1)
    
# for floating_ip in floating_ips_json["floatingips"]:
#     if floating_ip["tenant_id"] == project_id:
#         try:
#             r = requests.delete("%s/v2.0/floatingips/%s" % (neutron_endpoint.url,
#                                                             floating_ip["id"]),
#                                 headers=headers)
#             if r.status_code == 204:
#                 print "Floating IP %s has been released." % floating_ip["floating_ip_address"]
#         except requests.exceptions.RequestException as e:
#             print e
#             sys.exit(1)

# try:
#     security_groups = requests.get("%s/v2.0/security-groups" % neutron_endpoint.url,
#                                    headers=headers)
#     if security_groups.status_code == 200:
#         security_groups_json = json.loads(security_groups.text)
        
# except requests.exceptions.RequestException as e:
#     print e
#     sys.exit(1)
    
# for security_group in security_groups_json["security_groups"]:
#     if security_group["tenant_id"] == project_id:
#         try:
#             r = requests.delete("%s/v2.0/security-groups/%s" % (neutron_endpoint.url,
#                                                                 security_group["id"]),
#                                 headers=headers)
#             if r.status_code == 204:
#                 print "Security group %s has been deleted." % security_group["name"]
#         except requests.exceptions.RequestException as e:
#             print e
#             sys.exit(1)

# Glance: Deleting images

glance_endpoint = next(( endpoint for endpoint in catalog
                          if endpoint.service_id == "image"
                          and endpoint.interface == "public"), None)



