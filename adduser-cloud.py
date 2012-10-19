#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import requests
import json
from getpass import getpass
import ldap
import subprocess
import ConfigParser

def obtener_token(url,user,passwd):
    """
    Función que recibe el usuario y la contraseña de Keystone
    y devuelve el token de sesion
    """
    cabecera1 = {'Content-type': 'application/json'}
    datos = '{"auth":{"passwordCredentials":{"username": "%s", "password": "%s"}, "tenantName":"service"}}' % (user,passwd)
    solicitud = requests.post(url+'tokens', headers = cabecera1, data=datos)
    if solicitud.status_code == 200:
        token = json.loads(solicitud.text)["access"]["token"]["id"]
        return token
    else:
        print "Usuario y/o contraseña incorrecto/a"
        return ''   

def test_usuario(usuarios_cloud,usuario):
    """
    Función que comprueba si el usuario está o no en el objeto usuarios_cloud
    """
    for user in usuarios_cloud:
        if user["name"] == usuario:
            return 1
    return 0
    
# Se pasa como parámetro el nombre del usuario:
if len(sys.argv) == 2:
    usuario = sys.argv[1]
    print "Añadiendo el usuario %s al Cloud" % usuario
else:
    usuario = "*"

# Leemos los parámetros del fichero de configuración
config = ConfigParser.ConfigParser()
config.read("adduser-cloud.conf")
    
#Realizamos la conexión con el LDAP:
path = config.get("LDAP","path")
l = ldap.open(config.get("LDAP","ldap_server"))
bind_user = config.get("LDAP","bind_dn")
bind_pass = getpass("Password para admin de LDAP: ")
l.simple_bind_s(bind_user, bind_pass)
# Definimos una lista con 3 atributos (rdn del usuario, mail y atributo en el
# que se encuentra el hash SHA512 con sal)
lista_atrib = [config.get("LDAP","user_rdn_attrib"),
               'mail',config.get("LDAP","user_pass_attrib")]
# Filtramos los objetos que son inetOrgPerson y tienen 
filtro = '(&(objectClass=inetOrgPerson)(%s=*)(%s=%s))' % (lista_atrib[2], lista_atrib[0], usuario)
# El objeto LDAP usuarios_ldap es el resultado de la búsqueda
usuarios_ldap = l.search_s(path, ldap.SCOPE_SUBTREE, filtro, lista_atrib)
    
# Realizamos la conexión con keystone y obtenemos el token para la sesión
url = config.get("keystone","url")
while True:
    adminuser = raw_input("Usuario de Keystone: ")
    adminpass = getpass("Contraseña: ")
    admintoken = obtener_token(url,adminuser,adminpass)
    if len(admintoken) != 0:
        break

# Nos descargamos la lista de usuarios del cloud
cabecera = {'X-Auth-Token':admintoken,'Content-type': 'application/json'}
solicitud = requests.get(url+'users', headers = cabecera)
usuarios_cloud = json.loads(solicitud.text)["users"]

# Si el usuario existe, se actualiza. Si no existe se crea el usuario y el
# tenant del que es miembro (proy-...)
for usuario in usuarios_ldap:
    username = usuario[1]["uid"][0]
    # Comprobamos si existe el usuario
    if test_usuario(usuarios_cloud, username):
        # Actualizamos el usuario
        cont = 0
        for usuario_cloud in usuarios_cloud:
            if usuario_cloud["name"] == username:
                nuevo_pass = usuario[1]["%s"][0] % lista_atrib[2]
                userid = usuario_cloud["id"]
                print nuevo_pass, userid
                # subprocess.call("keystone --token %s --endpoint %s
                #                 user-password-update --pass %s --id %s" %
                #                 (admintoken, url, nuevo_pass, userid), shell = True)
                break
            else:
                cont += 1
                #        actualiza_usuario = requests.post(url+'users/{%s}' % userid, headers =
#                                          cabecera,data=payload)
#        if actualiza_usuario.status_code == 200:
#            id_usuario = json.loads(actualiza_usuario.text)["user"]["id"]
#            print "Actualizado el usuario %s con id %s" % (usuario[1]["uid"][0],id_usuario)
    else:
        # Creamos el usuario y el tenant
        payload = '{"user", {"name" : "%s", "email": "%s", "enabled" : True, "password": "%s"}}' % (usuario[1]["uid"][0], usuario[1]["mail"][0], usuario[1]["audio"][0])
        payload2 = '{"tenant", {"name" : "proy-%s", "description": "%s", "enabled" : True}}' % (usuario[1]["uid"][0], usuario[1]["uid"][0])
        # Añadimos cada usuario a la base de datos de keystone:
        nuevo_usuario = requests.post(url+'users', headers = cabecera,data=payload)
        if nuevo_usuario.status_code == 200:
            id_usuario = json.loads(nuevo_usuario.text)["user"]["id"]
            print "Creado el usuario %s con id %s" % (usuario[1]["uid"][0],id_usuario)
        else:
            print "No se ha creado el usuario %s" % usuario[1]["uid"][0]
            continue
        # Añadimos un tenant para cada usuario:
        nuevo_proy = requests.post(url+'tenants', headers = cabecera,data=payload2)
        if nuevo_proy.status_code == 200:
            id_proy = json.loads(nuevo_proy.text)["tenant"]["id"]
            print "Creado el tenant con id %s" % id_proy
        
        # En la versión 2.0 del API de keystone no es posible realizar operaciones
        # sobre roles o asignar un rol a un usuario en un tenant, tenemos que hacer
        # esto con el cliente keystone :-/
    
        # Ponemos el id de Member a "mano": 414fd98137754204bc61fad1d40cbdbc
        member_id = "414fd98137754204bc61fad1d40cbdbc"
        
        subprocess.call("keystone --token %s --endpoint %s user-role-add --user %s --role %s --tenant_id %s" % (admintoken, url, id_usuario, member_id, id_proy), shell = True)
