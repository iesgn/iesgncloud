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
	#borrar_volumenes
	#borrar_instantaneasInstancias(Miguel Angel Ávila Ruiz)
	#borrar_volumenes (Miguel Ángel Ávila Ruiz)
	for i in `nova volume-list |grep -v ^\+|grep -v ID| awk '{print $2}'`;
		do `nova volume-delete $i` ;
		echo "Eliminado el volumen " $i
	done
	#borrar_instantaneasvolumen(Jose Alejandro Perea)
	for i in `cinder snapshot-list | grep -v ^\+|grep -v ID | awk '{print $2}'`;
	do 
		`cinder snapshot-delete $i`;
		echo "Eliminadas las instantaneas de volumenes"
	done
	#borrar_imagenes
	
	#borrar_instancias(Fracnisco Javier Gimenez)
	for i in nova list | grep -v ^\+|grep -v ID | awk '{print $2}';
	do 
		nova delete $i;
	done	
	
	#borrar_proyecto(Fracnisco Javier Gimenez)
	#borro todos los proyectos de un usuario
	for i in '${tenants[*]}';
	do
		nova scrub $i;
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
