import winreg as _winreg
import os
from ctypes import c_int32,c_uint32

#-------------------General Helper Functions----------------------------
    
def SavePathToRegistry(pathkey, val, appname="\\Pydro", bLocalMachine=0, exData=0):
    if bLocalMachine:
        rootkey=_winreg.HKEY_LOCAL_MACHINE
    else:            
        rootkey=_winreg.HKEY_CURRENT_USER
    key=_winreg.CreateKey(rootkey,"SOFTWARE\\Tranya"+appname)
    if exData:
        _winreg.SetValueEx(key, pathkey, 0, _winreg.REG_SZ, val)
    else:
        _winreg.SetValue(key, pathkey, _winreg.REG_SZ, val)

def GetPathFromRegistry(pathkey, defaultval, appname="\\Pydro", bLocalMachine=0, exData=0):
    if bLocalMachine:
        rootkey=_winreg.HKEY_LOCAL_MACHINE
    else:            
        rootkey=_winreg.HKEY_CURRENT_USER
    try:
        key= _winreg.CreateKey(rootkey,"SOFTWARE\\Tranya"+appname)
        if exData:
            val,type_id= _winreg.QueryValueEx(key, pathkey)
        else:
            val= _winreg.QueryValue(key, pathkey)
        if not val: val=defaultval    # protect against key data = (value not set)
    except:
        val=defaultval
    return val

def SaveDWORDToRegistry(name, DWordName, val, bLocalMachine=0, keypathbase="SOFTWARE\\Tranya\\", appname=''):
    if bLocalMachine:
        rootkey=_winreg.HKEY_LOCAL_MACHINE
    else:            
        rootkey=_winreg.HKEY_CURRENT_USER
    if keypathbase[-1]!="\\": keypathbase+="\\"
    if appname: 
        if appname[-1]!='\\': appname+='\\'
    key=_winreg.CreateKey(rootkey,keypathbase+appname+name)
    _winreg.SetValueEx(key, DWordName, 0, _winreg.REG_DWORD, c_uint32(val).value)

def GetDWORDFromRegistry(name, DWordName, default=-999, bSilent=0, bLocalMachine=0, keypathbase="SOFTWARE\\Tranya\\", appname=''):
    if bLocalMachine:
        rootkeyStr,rootkey="HKEY_LOCAL_MACHINE",_winreg.HKEY_LOCAL_MACHINE
    else:            
        rootkeyStr,rootkey="HKEY_CURRENT_USER",_winreg.HKEY_CURRENT_USER
    try:
        if keypathbase[-1]!="\\": keypathbase+="\\"
        if appname: 
            if appname[-1]!='\\': appname+='\\'
        key=_winreg.CreateKey(rootkey,keypathbase+appname+name)
        regval=_winreg.QueryValueEx(key, DWordName)
        return c_int32(regval[0]).value
    except EnvironmentError:
        if not bSilent: print("Key didn't exist %s\\%s"%(rootkeyStr,keypathbase)+name+"\\"+DWordName)
        return default

def AddMITool(ToolPath, ToolName, Description="", Autoload=1, removeTool=""):
    try:
        bkey=_winreg.OpenKey(_winreg.HKEY_CURRENT_USER,r"SOFTWARE\MapInfo\MapInfo\Professional")
        numsubkeys,numvalues,lastmodified = _winreg.QueryInfoKey(bkey)
        for i in range(numsubkeys):
            tools=[]
            subbkeystr=str(_winreg.EnumKey(bkey,i))
            key=_winreg.OpenKey(_winreg.HKEY_CURRENT_USER,r"SOFTWARE\MapInfo\MapInfo\Professional\%s\Tools"%subbkeystr)
            numsubkeys,numvalues,lastmodified = _winreg.QueryInfoKey(key)
            for i in range(numsubkeys-1,-1,-1):
                subkeystr=str(_winreg.EnumKey(key,i))
                subkeyint=int(subkeystr)
                tools.append(subkeyint) #make a sequence for the max function to work on
                if removeTool:
                    subkey=_winreg.OpenKey(key,subkeystr)
                    pth=_winreg.QueryValueEx(subkey, "Location")[0].lower()
                    if pth.find(removeTool.lower())>=0: #remove old version of Tool
                        _winreg.DeleteKey(_winreg.HKEY_CURRENT_USER,r"SOFTWARE\MapInfo\MapInfo\Professional\%s\tools"%subbkeystr+"\\"+subkeystr)
                        tools.remove(subkeyint) # no reason to increment if existing MI key happens to be max
            maxk=max(tools)+1
            newkey=_winreg.CreateKey(_winreg.HKEY_CURRENT_USER,r"SOFTWARE\MapInfo\MapInfo\Professional\%s\tools"%subbkeystr+"\\"+str(maxk))
            _winreg.SetValueEx(newkey, "Location", 0, _winreg.REG_SZ, ToolPath)
            _winreg.SetValueEx(newkey, "Owner", 0, _winreg.REG_SZ, r"USER_DEFINED")
            _winreg.SetValueEx(newkey, "Title", 0, _winreg.REG_SZ, ToolName)
            _winreg.SetValueEx(newkey, "Autoload", 0, _winreg.REG_DWORD, Autoload)
            _winreg.SetValueEx(newkey, "Description", 0, _winreg.REG_SZ, Description)
    except WindowsError: # key path not found
        pass


# bridge a backward compatibility to any RegistryEnv_v1 data instance
class RegistryEnv():
    def __init__(self, appname='RegistryEnv', environment='Default', bLocalMachine=0):
        self.__oldkey = _winreg.CreateKey(_winreg.HKEY_CURRENT_USER,"SOFTWARE\\%s\\%s" % ('WesSoft','Default'))
        self.newkeyappname = "\\%s\\%s" % (appname,environment)
        self.bLocalMachine = bLocalMachine
    def get(self,value_name,value_def):
        value = self.__getitem__(value_name)
        return value if value else value_def
    def __getitem__(self,value_name):
        #handle class variables prefixed by "__"
        if 'RegistryEnv' in value_name:
            return self.__dict__[value_name]
        else:
            value = GetPathFromRegistry(value_name,"",self.newkeyappname,self.bLocalMachine,1)
            if not value:
                try:
                    value,type_id = _winreg.QueryValueEx(self.__oldkey,value_name)
                    SavePathToRegistry(value_name,value,self.newkeyappname,self.bLocalMachine,1)
                except: # problem with old -- who cares
                    pass
            return value
    def __setitem__(self,value_name, value):
        #handle class variables prefixed by "__"
        if 'RegistryEnv' in value_name:
            self.__dict__[value_name] = value
        else:
            SavePathToRegistry(value_name,value,self.newkeyappname,self.bLocalMachine,1)
    def __contains__(self,item):
            value = GetPathFromRegistry(item,"",self.newkeyappname,self.bLocalMachine,1)
            if not value:
                try:
                    value,type_id = _winreg.QueryValueEx(self.__oldkey,item)
                    SavePathToRegistry(item, value, self.newkeyappname, self.bLocalMachine,1)
                    return True
                except EnvironmentError:
                    return False
            else:
                return True
