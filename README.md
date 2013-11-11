# iesgncloud

Scripts and small applications used in IES GN OpenStack administradtion

## adduser-cloud

Used to create keystone users, extracting data from a LDAP tree. Each potential
keystone user must have a SHA512 hashed password created with crypt (e.g.
$6$lI4Cfr6S$nx/kWLPxMJzaAfoxTZYlFPv.kC49JobWHtvVCV5zrNHSffBEzqeQfP5.eZdVJwI1.XUeA3LeQ7Y8ZrW34900y1).

Particular parameters must be defined in adduser-cloud.conf