#!/usr/bin/python
# -*- coding: utf-8 -*-

#Eliminar todas las instanacias del usuario (Javier Giménez  ) Listo #
#Eliminar todos los snapshots del usuario (Miguel Ángel Ávila Ruiz) 
#Eliminar todos los volumenes del usuario (Adrian Cid Ramos) #
#Eliminar todas las instancias de voumenes del usuario (Jose Alejandro Perea García) #
#Liberar todas las ip flotantes del usuario (Carlos Miguel Hernández Romero) Completada
#Borra todos los pares de claves del usuario (Carlos Miguel Hernández Romero) Completada
#Borra todas las reglas de todos los grupos de seguridad del usuario (Adrián Jiménez)
#Borra todos los grupos de seguridad (Javier Giménez ) Listo
#Borra todoas las redes,subredes y routers del usuario (Adrián Cid Ramos)
<<<<<<< HEAD
#Borra el usuario del proyecto (Carlos Mejias) #
#Borra el proyecto(Miguel Angel Martin Serrano) Listo #
=======
#Borra el usuario del proyecto (Miguel Angel Martin) 
#Borra el proyecto(Carlos mejias) #
>>>>>>> c68a3d9d64e67a1bb82e140d8810f274f332f5c1

#Eliminar todas las imágenes del usuario (esta no la puso Alberto pero no esta de más hacerla) #


import sys
from getpass import getpass
import ConfigParser
from keystoneclient.v2_0 import client as keystonec
from novaclient.v1_1 import client as novac
from cinderclient import client

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


###############################################################################
# Orden en que llamaremos a las funciones pra realizar el boorado             #
# Cuando esten listos los procedimiento id poniendolso en su sitio            #
# Si se detecta algun error corregidolo cuando lo veais y dejad un comentario #
###############################################################################

# borrar reglas de lso grupos de seguridad
borrar_grupos()# borrar grupos de seguridad
borrar_pares_de_claves# borrar pares de claves
# borrar redes y sub redes
borrar_IPs_flotantes()# borrar ip flotantes
# Borrar snaptshots
# borrar isntancias de volúmenes
# borrar volumenes
# borrar imágenes ###########   falta por asignar    ##########
borrar_instancias() #borrar instancias
# borrar proyecto
# borrar usuario

############################################################################
# a continuación  estan los metodos para borrar algunos de los elementos   #
# hay que probarlos y incluirlos a cada uno en un procedimiento            #
############################################################################


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
def borrar_grupos():
	grupos=nova.security_groups.list()
	if len(grupos)==0:
		print "No tiene ningun grupo"
	else:
		for i in grupos:
			nova.security_groups.delete(i)

#Esta parte funciona
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
	listar=nova.volume_snapshots.list()
	if len(listar)==0:
		print "El usuario no tiene ninguna instantanea de volumen"
	else:
		for i in listar: 
			nova.volume_snapshots.delete(i)


#tiene que funcionar, pero no lo he probado para no borrarla
#Borra todos los pares de claves del usuario.
def borrar_pares_de_claves():
    keypairs=nova.keypairs.list()

    if len(keypairs)==0:
        print "No tiene pares de claves"

    else:
        for i in range(len(keypairs)): 
            nova.keypairs.delete(nova.keypairs.list()[i])
            print "Eliminada el par de claves %s" % str(keypairs[i])[10:].replace(">",'')

# borrar volumenes


def borrar_volumenes():
	cinder = client.Client('1', $user, $password, $tenant, $keystoneurl)
	listvol=cinder.volumes.list()
	
	if len(listvol)==0;
		print "No existen volumenes"
	else i in range(len(listvol));
		cinder.listvol.delete(cinder.listvol.list()[i])

#tiene que funcionar, pero no lo he probado para no borrarla
#Liberar todas las ip flotantes del usuario

def borrar_IPs_flotantes():
    ipflota=nova.floating_ips.list()

    if len(ipflota)==0:
        print "No tiene IPs flotantes"

    else:
        for i in range(len(ipflota)): 
            nova.floating_ips.delete(nova.floating_ips.list()[i])
            print "Eliminada la IP flotante %s" % ipflota[i].ip

#Borrar usuario 

from keystoneclient.v2_0 import keystonec
keystone = keystonec.Client(username = user,
                      password = password,
                      auth_url = keystoneurl)
del_user = keystone.users.delete(user)


