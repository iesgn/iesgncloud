#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import ConfigParser
from novaclient.v1_1 import client as novac
from cinderclient import client as cinderc
from neutronclient.neutron import client as neutronc
from keystoneclient.v2_0 import client as keystonec
from glanceclient.v2 import client as glancec
from credentials import get_keystone_creds
from credentials import get_nova_creds

if len(sys.argv) == 2:
    tenant_id = sys.argv[1]
    print "Deleting tenant %s and all related infrastructure from OpenStack" % tenant_id
else:
    print """
    Please use:
    $ deluser-cloud <tenant_id>
    """
    sys.exit()

config = ConfigParser.ConfigParser()
config.read("adduser-cloud.conf")

# Getting auth token from keystone
try:
    keystone_creds = get_keystone_creds()
    keystone = keystonec.Client(**keystone_creds)
except keystonec.exceptions.Unauthorized:
    print "Invalid keystone username or password"
    sys.exit()

nova_creds = get_nova_creds()
nova = novac.Client(**nova_creds)
neutron = neutronc.Client('2.0', **keystone_creds)
cinder = cinderc.Client('2',**nova_creds)
glance_endpoint = keystone.service_catalog.url_for(service_type='image',
                                                   endpoint_type='publicURL')
glance = glancec.Client(glance_endpoint, token=keystone.auth_token)

# Deleting nova servers

for server in nova.servers.list(search_opts={'all_tenants':1}):
    if server.tenant_id == tenant_id:
        server.delete()
            
# Deleting security groups

for sec_group in neutron.list_security_groups()['security_groups']:
    if sec_group['tenant_id'] == tenant_id:
        neutron.delete_security_group(sec_group['id'])

# Deleting floating IPs

for ip in neutron.list_floatingips()['floatingips']:
    if ip['tenant_id'] == tenant_id:
        neutron.delete_floatingip(ip['id'])

# Deleting routers

for router in neutron.list_routers()['routers']:
    if router['tenant_id'] == tenant_id:
        neutron.remove_gateway_router(router['id'])
    for port in neutron.list_ports(tenant_id=tenant_id)["ports"]:
        if port["device_id"] == router["id"]:
            neutron.remove_interface_router(router["id"],{'port_id':port["id"]})
    if router['tenant_id'] == tenant_id:
        neutron.delete_router(router['id'])

# Deleting subnetworks

for subnet in neutron.list_subnets()['subnets']:
    if subnet['tenant_id'] == tenant_id:
        neutron.delete_subnet(subnet['id'])

# Deleting networks

for network in neutron.list_networks()['networks']:
    if network['tenant_id'] == tenant_id:
        neutron.delete_network(network['id'])

# Deleting volume snapshots

for vol_snap in cinder.volume_snapshots.list(search_opts={'all_tenants':1}):
    if vol_snap.project_id == tenant_id:
        cinder.volume_snapshots.delete(vol_snap)

# Deleting volumes

for vol in cinder.volumes.list(search_opts={'all_tenants':1}):
    if vol._info['os-vol-tenant-attr:tenant_id'] == tenant_id:
        cinder.volumes.delete(vol)

# Deleting images

for image in glance.images.list(search_opts={'all_tenants':1}):
    if image['owner'] == tenant_id:
        glance.images.delete(image['id'])

# Borrar usuarios del proyecto
# Borrar proyecto

