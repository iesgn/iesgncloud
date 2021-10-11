#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Python script used to delete a project from a domain, including the deletion
of the following objects:
 * nova: instances
 * cinder: volume snapshots, volume backups and volumes
 * neutron: floating IPs, security groups, networks ,subnetworks and routers
"""
import sys
import configparser
from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client as keystonec
from neutronclient.v2_0 import client as neutronc
from novaclient import client as novac
from cinderclient import client as cinderc
from glanceclient import client as glancec
from credentials import get_keystone_v3_creds
import time

if len(sys.argv) == 2:
    project_id = sys.argv[1]
    print ("Deleting project %s and all related objects" % project_id)
else:
    print ("""
    Usage:
    deleteproject <project_id>
    """)
    sys.exit(1)

config = configparser.ConfigParser()
config.read("adduser-cloud.conf")

# Getting auth token from keystone with a session

try:
    creds = get_keystone_v3_creds()
    auth = v3.Password(**creds)
    sess = session.Session(auth=auth)
    keystone = keystonec.Client(session=sess)
except keystonec.exceptions.Unauthorized:
    print ("Invalid keystone username or password")
    sys.exit(1)

# Verifying admin role for user
try:
    keystone.users.list()
except keystonec.exceptions.Forbidden:
    print ("You are not authorized to run this script, admin role needed")
    sys.exit()

# Getting domain
try:
    domain = keystone.domains.find(
        name=config.get("default","domain"))
except keystonec.exceptions.NotFound:
    print ("Domain not found")
    sys.exit(1)

### Nova: Deleting all servers

nova = novac.Client(2.1, session=sess, endpoint_type='internalURL')

## Loading the list of servers and requesting to delete them
try:
    servers = nova.servers.list(search_opts={'all_tenants':True, 'project_id':project_id})
    for server in servers:
        try:
            nova.servers.delete(server)
            print ("Server %s deleted" % server.name)
        except novac.exceptions.NotFound as e:
            print (e)
            sys.exit(1)
except novac.exceptions.ClientException as e:
    print (e)
    sys.exit(1)

## Loading the list of server groups and requesting to delete them
# try:
#     server_groups = nova.server_groups.list(search_opts={'all_tenants':True)

#     for server in servers:
#         try:
#             nova.servers.delete(server)
#         except novac.exceptions.NotFound as e:
#             print e
#             sys.exit(1)

# except requests.exceptions.RequestException as e:
#     print e
#     sys.exit(1)

### Cinder: Deleting snapshots and volumes

cinder = cinderc.Client('3', session=sess, endpoint_type = 'internalURL')

## Loading the list of snapshots and requesting to delete them
try:
    snapshots = cinder.volume_snapshots.list(search_opts={'all_tenants':True,
                                                          'project_id':project_id})
    for snapshot in snapshots:
        try:
            cinder.volume_snapshots.delete(snapshot)
            print ("Snapshot %s deleted" % snapshot.name)
        except cinderc.exceptions.NotFound as e:
            print (e)
            sys.exit(1)
except cinderc.exceptions.ClientException as e:
    print (e)
    sys.exit(1)

# Waiting until there were no snapshots available, because a volume can't be deleted
# while any associated snapshot exists

while True:
    if len(snapshots) == 0:
        break
    else:
        print ("Waiting until associated snapshots are deleted ...")
        time.sleep(5)

## Loading the list of volume backups and requesting to delete them
try:
    backups = cinder.backups.list(search_opts={'all_tenants':True, 'project_id':project_id})
    for backup in backups:
        try:
            cinder.backups.delete(backup)
            print ("Backup %s deleted" % backup.name)
        except cinderc.exceptions.NotFound as e:
            print (e)
            sys.exit(1)
except cinderc.exceptions.ClientException as e:
    print (e)
    sys.exit(1)

## Loading the list of volumes and requesting to delete them
try:
    volumes = cinder.volumes.list(search_opts={'all_tenants':True, 'project_id':project_id})
    for volume in volumes:
        try:
            cinder.volumes.delete(volume)
            print ("Volume %s deleted" % volume.name)
        except cinderc.exceptions.NotFound as e:
            print (e)
            sys.exit(1)
except cinderc.exceptions.ClientException as e:
    print (e)
    sys.exit(1)

# Neutron: Deleting routers, subnets, networks, security groups and releasing floating IPs

neutron = neutronc.Client(session = sess,
                          project_id = project_id,
                          endpoint_type = 'internalURL')

# Deleting all security groups but default

for sec_group in neutron.list_security_groups()['security_groups']:
    if sec_group['project_id'] == project_id and sec_group['name'] != "default":
        neutron.delete_security_group(sec_group['id'])
        print ("Security group %s deleted" % sec_group['id'])

# Deleting floating IPs

for ip in neutron.list_floatingips()['floatingips']:
    if ip['project_id'] == project_id:
        neutron.delete_floatingip(ip['id'])
        print ("Floating IP %s released" % ip['floating_ip_address'])

# Deleting routers

for router in neutron.list_routers()['routers']:
    if router['project_id'] == project_id:
        neutron.remove_gateway_router(router['id'])
        for port in neutron.list_ports(project_id=project_id)["ports"]:
            if port["device_id"] == router["id"]:
                neutron.remove_interface_router(router["id"],{'port_id':port["id"]})
        if router['project_id'] == project_id:
            neutron.delete_router(router['id'])
            print ("%s deleted" % router['name'])

# Deleting ports

for port in neutron.list_ports()['ports']:
    if port['project_id'] == project_id and port['device_owner'] == 'compute:nova':
        neutron.delete_port(port['id'])
        print ("Port %s deleted" % port['name'])

# Deleting subnetworks

for subnet in neutron.list_subnets()['subnets']:
    if subnet['project_id'] == project_id:
        neutron.delete_subnet(subnet['id'])
        print ("Subnetwork %s deleted" % subnet['id'])

# Deleting networks

for network in neutron.list_networks()['networks']:
    if network['project_id'] == project_id:
        neutron.delete_network(network['id'])
        print ("%s deleted" % network['name'])

### Glance: Deleting images

# Getting glance's internal endpoint

service_id = keystone.services.find(name='glance').id
endpoint_url = keystone.endpoints.find(service_id = service_id,
                                       interface='internal').url
glance = glancec.Client('2', session = sess, endpoint = endpoint_url)

for image in glance.images.list():
    if image["owner"] == project_id:
        glance.images.delete(image["id"])
        print ("Image %s deleted" % image["name"])

## Unassign all roles to all the users in project_id and delete project

role_assignments = keystone.role_assignments.list()

for role_a in role_assignments:
    if 'project' in role_a.scope.keys() and role_a.scope['project']['id'] == project_id:
        keystone.roles.revoke(role_a.role['id'],
                              user = role_a.user['id'],
                              project = project_id)
        print ("Unassigning user roles")

### Delete the project
keystone.projects.delete(project_id)
print ("Project %s deleted" % project_id)

sys.exit(0)
