##Download a text file describing what patches to download and apply.
##Patch instructions must be in order that they'd be applied (oldest to newest) for RTP to work
#Format -
#Line1: Version (Constants.GetVersion()) it applys to (comma separated for multiple versions to update)
#Line2: Version it results in after application
#Line3: Size in Kb (comma separated for multiple versions to update)
#Line4: URL for patch file

#This Script downloads and parses the file building a dictionary of rtp commands 

import os
import win32api
import distutils.sysconfig
import urllib
#import pysvn #pysvn has no 64bit client so this has to be moved to a different location that can be run from 32bit python
import Constants
import string
import wx
import RegistryHelpers
try:
    import Gavana.GenericMessageDialog as GMD
except:
    import wx.lib.agw.genericmessagedialog as GMD
        

import socket
#import urllib2
# timeout in seconds
timeout = 5
socket.setdefaulttimeout(timeout)

import HSTPBin
bindir = HSTPBin.__path__[0]
pkg_dir = os.path.split(bindir)[0]

import distutils.sysconfig
PathToSitePkgs=distutils.sysconfig.get_python_lib()    
PathToPydro = pkg_dir+"\\HSTP\\Pydro" #'G:\\PydroTrunk\\Python27_x86\\Lib\\site-packages\\HSTP\\Pydro'

def WantAutoUpdate():
    if RegistryHelpers.GetDWORDFromRegistry("Pydro\\Preferences", "AutoUpdate", 1, bSilent=1):
        try:
            os.remove(PathToPydro+"\\NoUpdates.txt")
        except:
            pass
        try:
            batch=open('update.txt', 'r')
            print 'Update already in progress, resuming update'
        except:
            return True #file doesn't exist -- go ahead and look for new update
    else:
        open(PathToPydro+"\\NoUpdates.txt", "w+")
    return False

def GetUpdateText():
    try:
        #changing update to use selective directories, rather than full update of all folders -- use updateFolders.txt
        g='http://svn.pydro.noaa.gov/updatesFolders.txt' #don't use .py extension or web server tries to execute script and returns error.
        r=urllib.urlopen(g).read()
        r =map(string.strip, r.replace('\r\n','\n').split('\n'))
        for i in range(len(r)-1, -1, -1):
            if not r[i] or r[i][0]=='#': del r[i]
        return r
    except:
        print 'Could not connect to http://svn.pydro.noaa.gov'
        return []

def ProcessUpdate(updatelist):
    '''Process the instruction format into a dictionary that lists the patches to apply based on version of pydro.
        example dict  d = {origVer:[newVer,[(url, size, dest, ver), (url2,size2, dest2, ver2)]]}
        The tuples are processed in order so the last tuple of the instruction list is the version number pydro will
        be upgraded to.
    '''
    d={}
    lines_per_update = 6
    while len(updatelist)>=lines_per_update:
        oldver_all, newver, patch_size, svn_url, local_dir, recurse = updatelist[:lines_per_update]
        del updatelist[:lines_per_update]
        patchsizes=patch_size.split(',')
        for i, oldver in enumerate(oldver_all.split(',')):
            try: #allows multiple folder updates per version but they must be listed in seperate stanzas
                d[oldver].append([newver, svn_url, patchsizes[i], local_dir, recurse])
            except:
                d[oldver] = [[newver, svn_url, patchsizes[i], local_dir, recurse]]
    return d    

    
def CreateUpdateFile(d, k):
    if d.has_key(k): #there is an update to retrieve
        #determine the size and which updates to download if user chooses to update.
        tot, svn_url = 0, ''
        up_to_ver = k
        while d.has_key(up_to_ver):
            for newver, svn_url, sz, local_dir, recurse in d[up_to_ver]:
                if up_to_ver == newver: #stop infinite loop of version -- no update allowed or it will try to apply every time Pydro is run
                    break
                tot+=int(sz)
            if up_to_ver == newver: #stop infinite loop of version -- no update allowed or it will try to apply every time Pydro is run
                break
            up_to_ver = newver
        downloadver='%s\n -- download is %dKb\n'%(up_to_ver,tot)
        #Constants.PydroVersion()

        dlg = GMD.GenericMessageDialog(None, 'There is an update available for Pydro from\n%s to version\n'%k+downloadver+
                                '\nWould you like to download now?'+
                                '\n(Press HELP for a list of changes.',
                                'Newer Version Available', wx.YES_NO  | wx.CENTRE | wx.ICON_QUESTION, None) #| wx.HELP
        
        #dlg.SetIcon(self.GetIcon())
        confirm =  dlg.ShowModal()
        dlg.Destroy()
        
        if confirm in (wx.ID_YES,  wx.YES):
            #create a file specifying what version we are currently on and what the target version is as well as svn_url
            batch=open('update.txt', 'wb+')
            up_to_ver = k
            while d.has_key(up_to_ver):
                for newver, svn_url, sz, local_dir, recurse in d[up_to_ver]:
                    if up_to_ver == newver: #stop infinite loop of version -- no update allowed or it will try to apply every time Pydro is run
                        break
                    for l in ('0', up_to_ver, svn_url, local_dir, recurse):
                        batch.write('%s\n'%l)
                if up_to_ver == newver: #stop infinite loop of version -- no update allowed or it will try to apply every time Pydro is run
                    break
                up_to_ver = newver
            batch.close()

        else:
            print 'User declined update to ', newver
    else:
        #for ky,val in d.items():
        #    print ky, val
        print 'Pydro version ',k, 'No major updates available.'

def ClearVirtualStore():
    print "Checking for VirtualStore"
    PathToVirtualStore = os.path.expanduser("~\\AppData\\Local\\VirtualStore") #'C:\\Users\\barry.gallagher\\AppData\\Local\\VirtualStore'

    pth = os.path.splitdrive(PathToPydro)[1] #'\\PydroTrunk\\Python27_x86\\Lib\\site-packages\\HSTP\\Pydro
    PathToPydrosPython = "\\".join(os.path.normpath(pth).split("\\")[:-4]) #'\\PydroTrunk\\Python27_x86'
    if PathToPydrosPython:
        VirtStorePython = PathToVirtualStore+PathToPydrosPython #'c:\\users\\barry~1.gal\\appdata\\local\\temp\\10\\AppData\\Local\\VirtualStore\\PydroTrunk\\Python27_x86'
        #print PathToVirtualStore
        #print PathToPydrosPython
        #print VirtStorePython
        #raise Exception()
        if os.path.exists(VirtStorePython):
            print VirtStorePython+" was found"
            print """
            Windows 7 + I.T. policy have created a Virtual Store directory that 
            will prevent Pydro from running/updating properly.
            
            Pydro will attempt to remove this directory and hopefully updates will function normally.
            If continued odd behavior is observed, please contact HSTB."""
            import win32api
            from win32com.shell import shell, shellcon
            
            try:
                shell.SHFileOperation((0, shellcon.FO_DELETE, VirtStorePython, None, shellcon.FOF_ALLOWUNDO|shellcon.FOF_NOCONFIRMATION))
            except:
                print 
                print "Failed to remove ",VirtStorePython
                print "You may need an admin to remove this directory."
    else:
        print "Failed to determine install path for Pydro"
    

if __name__ == '__main__':
    #This function checks for updates to the source code using pysvn
    #As of Python 2.7 pysvn does not have a 64bit client so we have to separate the main python install 
    # from the 64bit packages.  The 32bit python is essentially limited to using built in modules and pysvn 
    # so the ClearVirtualStore function, for example, was moved into this module so it could use the win32api module.  
    
    if WantAutoUpdate():
        print "Checking for auto-update"
        #frame = wx.Frame(None)
        #frame.Show(False)
        #confirm = wx.MessageBox('Checking for updated version ',
        #                        'Connect to internet', wx.CENTRE | wx.ICON_INFORMATION, None)
        app = wx.App()
        app.MainLoop()
        update=GetUpdateText() #get the instructions from pydro.com
        if update:
            d=ProcessUpdate(update) #compile into a dictionary with the instructions per version
            k=Constants.PydroVersion()
            CreateUpdateFile(d, k)
            ClearVirtualStore()
    else:
        print "Auto-update turned off"
 