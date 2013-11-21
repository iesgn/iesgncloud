#!/usr/bin/python
# -*- coding: utf-8 -*-

#Eliminar todas las instanacias del usuario (Javier Giménez  )
#Eliminar todos los snapshots del usuario (Miguel Ángel Ávila Ruiz)
#Eliminar todos los volumenes del usuario (Adrian Cid Ramos)
#Eliminar todas las instancias de voumenes del usuario (Jose Alejandro Perea García)
#Liberar todas las ip flotantes del usuario (Carlos Miguel Hernández)
#Borra todos los pares de claves del usuario (Carlos Miguel Hernández)
#Borra todas las reglas de todos los grupos de seguridad del usuario
#Borra todos los grupos de seguridad (Javier Giménez )
#Borra todoas las redes,subredes y routers del usuario (Adrián Cid Ramos)
#Borra el usuario del proyecto
#Borra el proyecto(Miguel Angel Martin Serrano)

#Eliminar todas las mágenes del usuario (esta no la puso Alberto pero no esta de más hacerla)


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


#####################################################################################
# a continuación  estan los metodos para borrar algunos de los elementos
# hay que probarlos y incluirlos a cada uno en un procedimiento
#####################################################################################


# borrar una imagen 
#guardamos una lista con todas las imágenes

imagen = nova.images.list()
x=0

for i in imagen:
    print '{0}  {1}'.format(x, i)
    x=x+1

#seleccionamos la imagen
num=raw_input ('Selecione el número de la imagen a borrar')
#borramos la imagen
nova.images.delete(nova.images.list()[num])



#para borrar un grupo de seguridad

grupos=nova.security_groups.list()
x=0
for i in grupos:
	print '{0}  {1}'.format(x, i)
	x=x+1

if x==0:
	print "No tiene ningun grupo"

else:
	for i in range(x):
		nova.security_groups.delete( nova.security_groups.list()[num])

#Esta parte funciona
#borra todas las instacias

server=nova.servers.list()

x=0
for i in server:
    print '{0}  {1}'.format(x, i)
    x=x+1

if x==0:
    print "No tiene ninguna instancia"

else:
    for i in range(x): 
        nova.servers.delete(nova.servers.list()[i])


#tiene que funcionar, pero no lo he probado para no borrarla
#Borra todos los pares de claves del usuario.
keypairs=nova.keypairs.list()

x=0
for i in keypairs:
    print '{0}  {1}'.format(x, i)
    x=x+1

if x==0:
    print "No tiene pares de claves"

else:
    for i in range(x): 
        nova.keypairs.delete(nova.keypairs.list()[i])


#tiene que funcionar, pero no lo he probado para no borrarla
#Liberar todas las ip flotantes del usuario
ipflota=nova.floating_ips.list()

x=0
for i in ipflota:
    print '{0}  {1}'.format(x, i)
    x=x+1

if x==0:
    print "No tiene IPs Flotantes"

else:
    for i in range(x): 
        nova.floating_ips.delete(nova.floating_ips.list()[i])

#Borrar usuario 
#tengo que ver como autenticarme en keystone

from keystoneclient.v2_0 import client
keystone = client.Client(...)
tenants = keystone.tenants.list()
my_tenant = [x for x in tenants if x.name=='openstackDemo'][0]
my_user = keystone.users.delete(name="user",
	password="password",
	tenant_id=my_tenant.id)


