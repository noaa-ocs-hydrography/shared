#!/usr/bin/python
'''posixreg.py

James Hiebert <james.hiebert@noaa.gov>
February 21, 2007

NOAA's in-house Pydro software functions heavily on saving and recalling
values from the Windows registry.  The functions below substitute for a
windows-like registry on POSIX systems, by creating a hash tree of the
keys and then just writing it to disk (with python's pickler class for
object serialization)

You _must_ call posixreg.__init__() after import to inialize the global registry
'''

import os, sys
from sys import stderr
from pickle import Pickler, Unpickler, PicklingError, UnpicklingError

# Default path for registry is in the user's home directory
default_file = os.environ['HOME'] + os.sep + '.pydro.reg'
__all__ = ['posixreg', 'SavePathToRegistry', 'GetPathFromRegistry', 'SaveDWORDToRegistry', 'GetDWORDFromRegistry',
           'AddMITool']
class posixreg:
    def __init__(self, file=default_file):

        dir = os.sep.join(file.split(os.sep)[0:-2]) # Chop of the filename to get the directory

        if os.path.exists(file):
            self.file = file
            self.read_from_disk()
            sys.stderr.write("Registry file already exists, so I've read in the initial registry")
            sys.stderr.write(self.reg)
        elif os.path.exists(dir):
            self.file = file
            self.reg = {}
        else:
            sys.stderr.write("Warning: posixreg.__init__() received bad filename: {}".format(file))
            return None

    def write_to_disk(self):
        try:
            p = Pickler(open(self.file, 'w'))
            p.dump(self.reg)
        except PicklingError:
            sys.stderr.write("ERROR: could not save the registry to path {}".format(path))

    def read_from_disk(self):
        try:
            p = Unpickler(open(self.file, 'r'))
            self.reg = p.load()
        except UnpicklingError:
            sys.stderr.write("ERROR: could not load the registry from path {}".format(path))

    def get_value(self, key_path):
        '''recurses through the registry tree selecting the branch which
        matches the path, and returns the leaf entry.  Raises key error, if
        any component of the path does not exist
        '''
        keys = key_path.split('\\')

        current_reg = self.reg
        for k in keys:
            # skip double \\s
            if not k: continue
            try:
                current_reg = current_reg[k]
            except KeyError:
                if not k:
                    raise KeyError("path %s does not exist at component %s" % (key_path, k))
        return current_reg

    def put_value(self, key_path, value):
        path = key_path.split('\\')

        # Iterate through the entire registry path, stopping on the final
        current_reg = self.reg
        for p in path[0:-1]:
            if not p:
                continue
            if p not in current_reg:
                current_reg[p] = {}
                current_reg = current_reg[p]
            else:
                current_reg = current_reg[p]

        # Save the value to the last entry in the path
        current_reg[path[-1]] = value
        self.write_to_disk()

# Create a global registry that applications can use
reg = None
def __init__():
  global reg
  reg = posixreg()

def SavePathToRegistry(pathkey, val, appname="\\Pydro", bLocalMachine=0, keybasepath="SOFTWARE\\Tranya"):
    global reg
    if bLocalMachine:
        rootkey='HKEY_LOCAL_MACHINE'
    else:
        rootkey='HKEY_CURRENT_USER'

    reg.put_value('\\'.join([rootkey, keybasepath, appname, pathkey]), val)

def GetPathFromRegistry(pathkey, defaultval, appname="\\Pydro", bLocalMachine=0, keybasepath="SOFTWARE\\Tranya"):
    global reg
    if bLocalMachine:
        rootkey='HKEY_LOCAL_MACHINE'
    else:
        rootkey='HKEY_CURRENT_USER'

    try:
      val = reg.get_value('\\'.join([rootkey, keybasepath, appname, pathkey]))
      if not val: raise Exception()
    except:
      val = defaultval

    return val

def SaveDWORDToRegistry(name, DWordName, val, bLocalMachine=0, keypathbase="SOFTWARE\\Tranya\\", appname=''):
    if bLocalMachine:
        rootkey='HKEY_LOCAL_MACHINE'
    else:
        rootkey='HKEY_CURRENT_USER'

    reg.put_value('\\'.join([rootkey, keypathbase, appname, name, DWordName]), val)

def GetDWORDFromRegistry(name, DWordName, default=-999, bSilent=0, bLocalMachine=0, keypathbase="SOFTWARE\\Tranya\\", appname=''):
    if bLocalMachine:
        rootkey='HKEY_LOCAL_MACHINE'
    else:
        rootkey='HKEY_CURRENT_USER'
    return reg.get_value('\\'.join([rootkey, keypathbase, appname, name, DWordName]))

def AddMITool(ToolPath, ToolName, Description="", Autoload=1, removeTool=""):
    raise NotImplementedError("AddMITool not yet available for non-windows platforms")



# Run this file explicity to run this test
if __name__ == '__main__':
    print('Testing posixreg.py')
    print('Default file is: {}'.format(default_file))

    print('\nInitializing a posixreg object with a bad path')
    r = posixreg('/this/path/does/not/exist')

    print('\nInitializing a posixreg object where the directory exists, but the file does not')
    r = posixreg('/home/jamesmh/blah.stuff')

    print('\nTrying to initialize a valid posixreg object with the default path')
    r = posixreg()

    print('\nWriting an empty registry to disk')
    r.write_to_disk()
    print("  {}".format(r.reg))

    print('\nReading the empty registry back')
    r.read_from_disk()
    print("  {}".format(r.reg))

    print('\nAdding some arbitrary values')
    paths = ['blah\\stuff\\foo\\bar', 'blah\\\\stuff\\\\james\\hiebert', 'a\\completely\\different\\tree']
    vals  = [1, 2, 3]

    for i in range(3):
        print('  Adding: {}={}'.format(paths[i], vals[i]))
        r.put_value(paths[i], vals[i])

    print("\nHere's what the tree looks like after adding:")
    print("  {}".format(r.reg))

    print("\nTesting the retreive functions (these should match what's above")
    for i in range(3):
        print('  get_value(' + paths[i] + ') returns: {}'.format(r.get_value(paths[i])))

    print("\nNow write the full thing to disk")
    r.write_to_disk()
    r.reg = {}
    print("Blow it away: {}".format(r.reg))
    print("Read it back from disk")
    r.read_from_disk()
    print("And we should have the original back")
    print("  {}".format(r.reg))
