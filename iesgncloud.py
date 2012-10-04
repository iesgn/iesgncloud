import requests
import json
from getpass import getpass

admintoken = getpass("Introduce el token de Admin:")

cabecera = {'X-Auth-Token':admintoken,
            'Content-type': 'application/json'}

url = 'http://jupiter:35357/v2.0/'

# Para crear los usuarios directamente con los hashes de los passwords
# es necesario que estén en formato crypt SHA512 con sal (los que
# empiezan por $6$ en los sistemas linux

print("El fichero de usuarios debe tener el formato:")
print("nombre de usuario,email,contraseña en crypt sha512 con sal")
nom_fichero = raw_input("Nombre del fichero de usuarios: ")
f = open(nom_fichero,r)

for linea in f:
    campos=linea.split(',')
    payload = {"user": {"name": campos[0],
                        "email": campos[1],
                        "enabled": True,
                        "password": campos[2]}
               }
# Creamos un usuario por cada línea del fichero:
    r = requests.post(url+'users', headers = admintoken, data=json.dumps(payload))
    if r.status_code != 200:
        print ("Error con el usuario %s", campos[0])
        break

    
