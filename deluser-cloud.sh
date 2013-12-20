#!/bin/bash

#definir funcion borrar routers(Miguel Angel Martin Serrano)
function borrar_routers(){
echo "Borrando router del usuario"
	for routerid in `quantum router-list |grep -v ^\+| awk '{print $2}'| grep -v 'id'`;
        	do
        	tenant_router=`quantum router-show $routerid | grep tenant_id | awk '{print $4}'` ;
        	if tenant_router=id_tenant     
                then
                        quantum router-delete $routerid`;
                        echo "Eliminanando router: " $routerid
                else
                        echo "No se borra router: " $routerid
                fi
			done
}


	#borrar_instancias(Fracnisco Javier Gimenez)
function borrar_instancia(){

	for i in `nova list --all-tenants| grep -v ^\+|grep -v ID | awk '{print $2}'`;#recorremos todas las instancias
	do
		tnt_id = `nova show $i | grep tenant_id | awk '{print $4}';`# sacamos tenant de la instancia
		if [ $tnt_id -eq $id_tenant ];# si coinciden tenants borramos
			`nova delete $i`
		fi
	done
}

	#borrar_proyecto(Fracnisco Javier Gimenez)
function borrar_tenant();{
	`nova scrub $id_tenant;`
	`keystone tenant-delete $id_tenant;`
}


	#borrar_IPs_flotantes(Carlos Miguel Hernandez Romero)(Funciona)
function borrar_ipflotante(){
        for idipflota in `quantum floatingip-list |grep -v ^\+| awk '{print $2}'| grep -v 'id'`;
        do
            for idtenantip in `quantum floatingip-show $idipflota |grep -v ^\+| grep tenant_id| awk '{print $4}'| grep -v 'Value'`;
            do
                if idtenantip=id_tenant     
                then
                     do `quantum floatingip-delete $idipflota`;
                     echo "Eliminado la ipflotante con id: " $idipflota
                else
                    echo "No se ha podido eliminar la ipflotante con id: " $idipflota
                fi
        done
}



#Definir la variable usuario con el nombre de usuario en el argumento 1 del programa
usuario=$1
#Guardo la ubicación del fichero en la variable archivo por si la necesito más adelante
archivo=/openrc.sh
#Compruebo si existe
if [ -e $archivo ]
# Si existe lo cargo y procedo a eliminar el usuario
then
	#Carcargar variables de entorno
	source /openrc.sh

	# obtener ID de un usuario
	id=`keystone user-list | grep $1 |awk '{print $2}'`
	# Vector con todos los ID de proyectos
	tenants_id=(`keystone tenant-list |grep -v ^\+|grep -v id | awk '{print $2}'`)
	# Vector con todos los ID de usuarios
	users_id=(`keystone user-list |grep -v ^\+|grep -v id | awk '{print $2}'`)
	
	# Creo una lista con los tenants del usuario que deseamos borrar
	cont = 0;
	for idt in tenanats_id;
		do
			keystone role-list --user-id $id --tenant-id $idt
			if [ $? -eq 0 ]; then
				 user_tenant[ cont ] = $idt
				 (( cont += 1 ))
			fi
		done
	# Chekeo que en los tenants del usuario no haya más usuarios, si es así borro
	for id_tenant in user_tenant;
		do
			cont = 0
			for id_user in users_id;
			do
				keystone role-list --user-id $id_user --tenant-id $id_tenant
				if [ $? -eq 0 ]; then
				 (( cont += 1 ))
				fi
			done
			if [ $cont -lt 2 ]
				borrar_routers();
				#Meted aqui las llamadas a las funciones
				borrar_ipflotante();
				
				borrar_instancia();
				borrar_tenant();#este debe ser el último en ejecutase
		done






#Crear funciones al principio del documento y llamarlas donde esta indicado
	# obtener ID de un usuario
        id=`keystone user-list | grep $1 |awk '{print $2}'`
        #creo un vector con los proyectos del usuario
        tenants=(`keystone tenant-list | grep $1 | awk '{print $2}'`)
	#Borrar usuario
	echo -e "\nDeleting user "$usuario"...."
        keystone user-delete $usuario

	#Pasos que necesitamos en este programa(Asignarselos) -- Da un error cuando intentamos borrar un grupo
	#que esta en uso en alguna instancia. Por lo que habra que borrar antes la instancia.

	#borrar_grupos(Adrian Jimenez Blanes)
	for i in `nova secgroup-list |grep -v ^\+|grep -v Name| awk '{print $2}'`;
		do `nova secgroup-delete $i` ;
		echo "Eliminado el grupo de seguridad: "$i
	done

	#borrar_pares_de_claves(Carlos Miguel Hernandez Romero)(Funciona)
	for i in `nova keypair-list |grep -v ^\+|grep -v Name| awk '{print $2}'`;
		do `nova keypair-delete $i` ;
		echo "Eliminada el par de claves" $i
	done

	#borrar_subredes(Adrián Cid)
	
	for i in `quantum subnet-list |grep -v ^\+| awk '{print $2}'| grep -v 'id'`;
                do `quantum subnet-delete $i` ;
                echo "Eliminando todas las subnets: " $i
        done	
	
	#borrar_redes(Adrián Cid)

	for i in `quantum net-list |grep -v ^\+| awk '{print $2}'| grep -v 'id'`;
                do `quantum net-delete $i` ;
                echo "Eliminando todas las redes: " $i
        done	
	
	
	#borrar_routers(Miguel Angel Martin Serrano)
	for i in `quantum router-list |grep -v ^\+| awk '{print $2}'| grep -v 'id'`;
                do `quantum router-delete $i` ;
                echo "Eliminanando router: " $i
        done

	
	#borrar_instantaneasInstancias

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
	#borrar_imagenes (Carlos Mejías)
	for i in `nova image-list |grep -v ^\+|grep -v ID| awk '{print $2}'`;
	do
		`nova image-delete $i`;
		echo "Eliminada la imagen" $i
	done


# Si no existe le indico a el usuario el problema
else
	echo -e "No existe el archivo /openrc.sh es necesario para borrar el usuario"
	exit 0
fi
