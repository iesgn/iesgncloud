#!/bin/bash
#Definir la variable usuario con el nombre de usuario en el argumento 1 del programa
usuario=$1
# Pedir la contrasenna de usuario y guardar en la variable passwd
read -s -p "Please enter your OpenStack Password: " passwd
echo -e "\nDeleting user "$usuario"...."

#Pasos que necesitamos en este programa(Cada uno ya sabe que hizo en deluser-cloud.py)
#borrar_reglas
#borrar_grupos
#borrar_pares_de_claves
#borrar_subredes
#borrar_redes
#borrar_routers
#borrar_IPs_flotantes
#borrar_snapshos_volumenes
#borrar_volumenes
#borrar_instantaneasvolumen
#borrar_instantaneasvolumen
#borrar_imagenes
#borrar_instancias
#borrar_proyecto
#borrar_usuario
keystone user-delete $1
