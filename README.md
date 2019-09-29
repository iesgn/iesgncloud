# iesgncloud

Python scripts in the IES Gonzalo Nazareno OpenStack private cloud

## LDAP keystone domain

Since keystone v3, domains are available allowing different
authentication methods, in this case we're using a specific domain for
LDAP users. 

## createproject.py

This script creates a project for every user in the keystone LDAP
domain or to one user when specified. When the project is created, a
minimal network infrastructure is created: One network, one subnetwork
and one router.

## deleteproject.py

This script is used to remove all the elements related to one user
tenant (volumes, instances and network elements) and finally removes
the tenant.
