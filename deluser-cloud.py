#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from getpass import getpass
import ConfigParser
from novaclient.v1_1 import client as novac
from cinderclient import client as cinderc
from quantumclient.v2_0 import client as quantumc
from keystoneclient.v2_0 import client as keystonec

nova = novac.Client(username = user,
                    api_key = password,
                    project_id = tenant,
                    auth_url = keystoneurl)
                    
quantum = quantumc.Client(username = user,
                    api_key = password,
                    project_id = tenant,
                    auth_url = keystoneurl)

cinder = cinderc.Client(username = user,
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
    print "deleting ALL users and tenants except admin user an service tenant"

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

# Getting user list to delete
if user == "*":
    users_list = keystone.users.list()
else:
    users_list = [ keystone.users.find(name=user) ]

# Getting tenants of each user:
for tenant in keystone.tenants.list():
    for tenant_user in tenant.list_users():
        



############################################################################
# a continuación  estan los metodos para borrar algunos de los elementos   #
# hay que probarlos y incluirlos a cada uno en un procedimiento            #
############################################################################


#Borrar todas las imagenes
def borrar_imagenes():
	Borrartodas = nova.images.list()
	if leng(Borrartodas) == 0:
		print "No hay imagenes que borrar"
	else:
		for imagen in Borrartodas:
			try:
				nova.images.delete(imagen)
			except:
				print "No tienes permisos para borrar la imagen"
                                
#No hemos encontrado la forma de relacionar la imagen con un usuario en concreto, 
#asi que hemos utilizado un try para controlar el error en medida de lo posible.

#para borrar un grupo de seguridad
def borrar_grupos():
	grupos=nova.security_groups.list()
	if len(grupos)==0:
		print "No tiene ningun grupo"
	else:
		for i in grupos:
			nova.security_groups.delete(i)


#borra todas las instacias

def borrar_instancias():
	server=nova.servers.list()

	if len(server)==0:
		print "No tiene ninguna instancia"
	else:
		for i in server: 
			nova.servers.delete(i)

#Eliminar todas las instantaneas de volumenes del usuario
def borrar_instantaneasvolumen():
	listar=nt.volume_snapshots.list()
	if len(listar)==0:
		print "El usuario no tiene ninguna instantanea de volumen"
	else:
		for i in listar: 
			nt.volume_snapshots.delete(i)

#Borra todos los pares de claves del usuario.
def borrar_pares_de_claves():
    keypairs=nova.keypairs.list()

    if len(keypairs)==0:
        print "No tiene pares de claves"

    else:
        for i in range(len(keypairs)): 
            nova.keypairs.delete(keypairs[i].name)
            print "Eliminada el par de claves %s" % keypairs[i].name

# borrar volumenes

def borrar_volumenes():
	listvol=cinder.volumes.list()
	
	if len(listvol)==0:
		print "No existen volumenes"
	else:
		for i in range(len(listvol)):
			cinder.listvol.delete(i)
		
# Borra todas las redes,subredes y routers del usuario

def borrar_subredes():
	lissub=quantum.list_subnets()

	if len(lissub)==0:
		print "No hay subredes que borrar"
	else: 
		for i in range(len(listsub)):
			quantum.delete_subnet(quantum.subnets[i][id])

def borrar_redes():
	lisreds=quantum.list_networks()

	if len(lisreds)==0:
		print "No hay redes que borrar"
	else: 
		for i in range(len(listreds)):
			quantum.delete_network(quantum.networks[i][id])
		
def borrar_routers():
	lisrout=quantum.list_routers()

	if len(lisrout)==0:
		print "No hay routers que borrar"
	else:
		for i in range(len(listrout)):
			quantum.delete_router(quantum.routers[i][id])

#Liberar todas las ip flotantes del usuario

def borrar_IPs_flotantes():
    ipflota=nova.floating_ips.list()

    if len(ipflota)==0:
        print "No tiene IPs flotantes"

    else:
        for i in range(len(ipflota)): 
            nova.floating_ips.delete(ipflota[i].id)
            print "Eliminada la IP flotante %s" % ipflota[i].ip
            
            
# Borrar snaptshots
# Borrar snapshots de volumenes

def borrar_snapshos_volumenes():
	volsnap=cinder.volume_snapshots.list()
	
for i in volsnap:
    print '{0}  {1}'.format(x, i)
    x=x+1
    
if x==0:
    print "No existen snapshot de volumenes"
    
else:
    for i in range(x): 
        cinder.volume_snapshots.delete(cinder.volume_snapshots.list()[i]))
		print "Eliminado el snapshot del volumen %s" %

#Borrar proyecto

def borrar_proyecto():
        nombreproyectoaborrar=nova.project_id

if nombreproyectoaborrar:
        keystone.tenants.delete(nombreproyectoaborrar)
else:
        print "No hay ningun proyecto definido"
       
#Borrar usuario 

def borrar_usuario():
	for usuario in keystone.users.list():
		if usuario.name == user:
			 exists = True
		else
			break
	if exists == True:	
		print "Borrando usuario"
		keystone.users.delete(user)

# borrar reglas de los grupos de seguridad

def borrar_reglas():
    gruposyreglas = nova.security_groups.list()
    if len(gruposyreglas) == 0:
        print "No tiene ningun grupo, por lo tanto, no hay reglas."
    else:
       for i in xrange(0,int(len(gruposyreglas))):
           grupo = gruposyreglas[i]
	   reglas = grupo.rules
	   for i in xrange(0,int(len(reglas))):
	       nova.security_group_rules.delete(reglas[i]["id"])

###############################################################################
# Orden en que llamaremos a las funciones pra realizar el boorado             #
# Cuando esten listos los procedimiento id poniendolso en su sitio            #
# Si se detecta algun error corregidolo cuando lo veais y dejad un comentario #
###############################################################################

	       
borrar_reglas() # borrar reglas de los grupos de seguridad
borrar_grupos() # borrar grupos de seguridad
borrar_pares_de_claves# borrar pares de claves
borrar_subredes()# borrar redes y sub redes
borrar_redes()
borrar_routers()
borrar_IPs_flotantes() # borrar ip flotantes
borrar_snapshos_volumenes() # Borrar snaptshots
borrar_volumenes() # borrar volumenes
borrar_instantaneasvolumen()# borrar isntancias de volúmenes
borrar_instantaneasvolumen()
borrar_imagenes()# borrar imágenes
borrar_instancias() #borrar instancias
borrar_proyecto() # borrar proyecto
borrar_usuario()# borrar usuario
	       


