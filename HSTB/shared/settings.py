from sys import platform
if 'win' in platform:
  from .winreg import *

elif 'linux' in platform:
  from .posixreg import *
  init()
