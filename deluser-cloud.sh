#!/bin/bash
#Definir la variable usuario con el nombre de usuario en el argumetno 1 del programa
usuario=$1
# Pedir la contrasenna de usuario y guardar en la variable passwd
read -s -p "Please enter your OpenStack Password: " passwd
echo -e "\nDeleting user "$usuario"...."
