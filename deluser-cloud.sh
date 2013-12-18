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
	# obtener ID de un usuario 
	id=`keystone user-list | grep $1 |awk '{print $2}'`
	#creo un vector con los proyectos del usuario
	tenants=(`keystone tenant-list | grep $1 | awk '{print $2}'`)	
	
	#Pasos que necesitamos en este programa(Asignarselos) -- Da un error cuando intentamos borrar un grupo
	#que esta en uso en alguna instancia. Por lo que habra que borrar antes la instancia.

	#borrar_grupos(Adrian Jimenez Blanes)
	for i in `nova secgroup-list |grep -v ^\+|grep -v Name| awk '{print $2}'`;
		do `nova secgroup-delete $i` ;
	done

	#borrar_pares_de_claves(Carlos Miguel Hernandez Romero)(Funciona)
	for i in `nova keypair-list |grep -v ^\+|grep -v Name| awk '{print $2}'`;
		do `nova keypair-delete $i` ;
		echo "Eliminada el par de claves" $i
	done

	#borrar_IPs_flotantes(Carlos Miguel Hernandez Romero)(Funciona)
	for i in `nova floating-ip-list |grep -v ^\+|grep -v Ip| awk '{print $2}'`;
		do `nova floating-ip-delete $i` ;
		echo "Eliminada la IP flotante" $i
	done

        #borrar_subredes(Adrián Cid)
	#borrar_redes(Adrián Cid)
	#borrar_routers(Adrián Cid)(Si alguien la quiere que lo ponga aqui)
	#borrar_snapshos_volumenes
	#borrar_volumenes
	#borrar_instantaneasvolumen(Jose Alejandro Perea)
	#borrar_imagenes
	#borrar_instancias
	#borrar_proyecto(Fracnisco Javier Gimenez)
	#borro todos los proyectos de un usuario
	for i in '${tenants[*]}';
	do
		keystone tenant-delete $i;
	done
	#borrar_usuario(Miguel Angel Martin)
	echo -e "\nDeleting user "$usuario"...."
	keystone user-delete $usuario
# Si no existe le indico a el usuario el problema
else
	echo -e "No existe el archivo /openrc.sh es necesario para borrar el usuario"
	exit 0
fi
