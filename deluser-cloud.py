#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from getpass import getpass
import ConfigParser
from keystoneclient.v2_0 import client as keystonec
from novaclient.v1_1 import client as novac

# con el usuario bisharron podemos usar la api de forma estatica
# solo con este usuario

tenant = "proy-bisharron"
keystoneurl = "http://172.22.222.1:5000/v2.0"
user = "bisharron"
password = "asdasd"

nova = novac.Client(username = user,
                    api_key = password,
                    project_id = tenant,
                    auth_url = keystoneurl)



if len(sys.argv) == 2:
    user = sys.argv[1]
    print "Deleting user %s to OpenStack" % user
else:
    print """
    If you want to delete or modify ONLY ONE USER, please use:
    $ deluser-cloud <username>
    """
    if raw_input("Are you sure you want to continue (y/n)? ") != 'y':
        sys.exit()
    user = "*"
    print "deleting ALL users"

# Getting auth token from keystone

admintoken = ''
while len(admintoken) == 0:
    adminuser = raw_input("Keystone admin user: ")
    adminpass = getpass("Keystone admin user password: ")
    try:
        keystone = keystonec.Client(username=adminuser,
                                    password=adminpass,
                                    tenant_name=config.get("keystone","admintenant"),
                                    auth_url=config.get("keystone","url"))
        admintoken = keystone.auth_token
        
    except keystonec.exceptions.Unauthorized:
        print "Invalid keystone username or password"

#Eliminar todas las instanacias del usuario
#Eliminar todos los snapshots del usuario
#Eliminar todos los volumenes del usuario
#Eliminar todas las instancias de voumenes del usuario
#Liberar todas las ip flotantes del usuario
#Borra todos los pares de claves del usuario
#Borra todas las reglas de todos los grupos de seguridad del usuario
#Borra todos los grupos de seguridad
#Borra todoas las redes,subredes y routers del usuario
#Borra el usuario del proyecto
#Borra el proyecto


#para borrar un grupo de seguridad

nova.security_groups.delete( nova.security_groups.list()[0])

