# iesgncloud

Scripts and small python applications used in IES GN OpenStack administration

## adduser-cloud

Used to create keystone users and tenants, extracting data from a LDAP tree and putting then into a MySQL database. When a user
is created a minimal network infrastructure is created: One network, one subnetwork and one router. 

We don't like the way LDAP is implemented into OpenStack, IOHO it's a very "intrusive" method. We loved
a LDAP backend that can be used only for authentication purposes, allowing the utilization of all usernames and
password of our organization, but that until now has not been possible. 

## deluser-cloud

Used to remove a user from a tenant. If the user is the only user in the tenant, the program removes all elements related to this
tenant (volumes, instances and network elements) and finally removes the tenant.
