#!/bin/bash
#Definir la variable usuario con el nombre de usuario en el argumento 1 del programa
usuario=$1
#Guardo la ubicación del fichero en la variable archivo por si la necesito más adelante
archivo=/openrc.sh
#Compruebo si existe
if [ -e $archivo ]
# Si existe lo cargo y procedo a eliminar el usuario	
then
	source /openrc.sh
	#Pasos que necesitamos en este programa(Asignarselos)
	#borrar_grupos(Adrian Jimenez Blanes) -- Da un error cuando intentamos borrar un grupo 
	#que esta en uso en alguna instancia. Por lo que habra que borrar antes la instancia.
	for i in `nova secgroup-list |grep -v ^\+|grep -v Name| awk '{print $2}'`; 
	do `nova secgroup-delete $i` ; 
	done

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
	#borrar_usuario(Miguel Angel Martin)
	echo -e "\nDeleting user "$usuario"...."
	keystone user-delete $usuario
# Si no existe le indico a el usuario el problema
else
echo -e "No existe el archivo /openrc.sh es necesario para borrar el usuario"
exit 0
fi
