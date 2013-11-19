#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from getpass import getpass
import ConfigParser
from keystoneclient.v2_0 import client as keystonec
from quantumclient.quantum import client as quantumc

if len(sys.argv) == 2:
    user = sys.argv[1]
    print "Deleting user %s to OpenStack" % user
else:
    print """
    If you want to delete or modify ONLY ONE USER, please use:
    $ deluser-cloud <username>
    """
    if raw_input("Are you sure you want to continue (y/n)? ") != 'y':
        sys.exit()
    user = "*"
    print "deleting ALL users"

