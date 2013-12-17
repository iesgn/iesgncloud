#!/bin/bash
#Definir la variable usuario con el nombre de usuario en el argumento 1 del programa
usuario=$1
# Pedir la contrasenna de usuario y guardar en la variable passwd
archivo=/openrc.sh
if [ -e $archivo ]
then
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
	echo -e "\nDeleting user "$usuario"...."
	keystone user-delete $1
else
echo -e "No existe el archivo $archivo\n es necesario para borrar el usuario"
exit 0
fi
