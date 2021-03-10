from __future__ import print_function
#!/usr/bin/env python

import distutils.sysconfig
PathToSitePkgs = distutils.sysconfig.get_python_lib()
import subprocess
import sys
import time
from HSTB.versioning import upgrade
import os


def CallGetRevision(filename=""):  # mimics the old pysvn calls
    return GetRevision(filename)


def GetRevision(filename):
    client = upgrade.SlikSVNClient()
    return client.getRevision(filename)


if __name__ == '__main__':
    filename = sys.argv[1]
    exit(GetRevision(filename))
