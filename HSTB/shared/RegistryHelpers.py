'''Helper functions that get user filename/directory input and remember where they were loaded from and open in the same place next time
wx and qt dialogs are supported.  By setting os.environ["PYDRO_GUI"] to "wx" or "qt" that version will be the default implementation for
GetDirFromUser and GetFilenameFromUser
'''

import os
import sys

from .settings import *

# -----------------Cross-gui code-------------------
# @TODO use pathlib instead of os.path
# @TODO use pep8 naming conventions


def PathFromFilename(s):
    return os.path.split(s)[0]


def get_start_path(RegistryKey, DefaultVal, AppName, bLocalMachine):
    if RegistryKey:
        startpath = GetPathFromRegistry(RegistryKey, DefaultVal, AppName, bLocalMachine)
    elif os.path.exists(DefaultVal):
        startpath = DefaultVal
    else:
        startpath = "."
    return startpath


def save_start_path(RegistryKey, pathname, AppName, bLocalMachine):
    if RegistryKey:
        SavePathToRegistry(RegistryKey, pathname, AppName, bLocalMachine)


def GetDirFromUserWX(parent, RegistryKey=None, DefaultVal=".", Title="Browse for folder", Message="",
                     AppName="\\Pydro", bLocalMachine=0):
    '''Pops up a wx.DirDialog to get a directory from the user.
       Returns a two-item list [return code, pathname (or None)]
    '''
    startpath = get_start_path(RegistryKey, DefaultVal, AppName, bLocalMachine)

    dlg2 = wx.DirDialog(parent, Message, startpath)
    dlg2.SetTitle(Title)
    # dlg2.CentreOnParent()  # getting "'GetWindowRect' failed with error 0x00000578 (invalid window handle.)."
    rcode = dlg2.ShowModal()
    if rcode == wx.ID_OK:
        pathname = dlg2.GetPath()
        save_start_path(RegistryKey, pathname, AppName, bLocalMachine)
        ret = [rcode, pathname]
    else:
        ret = [rcode, None]
    return ret


def GetFilenameFromUserWX(parent, bSave=1, RegistryKey=None, DefaultVal=".", Title="Choose a path/filename", DefaultFile="", fFilter="All Files|*.*",
                          AppName="\\Pydro", bLocalMachine=0, bMulti=0, bReturnFileType=0):
    '''Pops up a wx.FileDialog to get a directory from the user.  Returns a
       two or three-item list [return code, filename (or None), optionally
       the wild-card 'save of type'] *JMH says that this should return a
       tuple instead
    '''
    startpath = get_start_path(RegistryKey, DefaultVal, AppName, bLocalMachine)

    if bSave:
        dstyle = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
    else:
        dstyle = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        if bMulti:
            dstyle |= wx.FD_MULTIPLE
    dlg = wx.FileDialog(parent, Title, startpath, DefaultFile, fFilter, style=dstyle)
    # dlg.CentreOnParent()   # getting "'GetWindowRect' failed with error 0x00000578 (invalid window handle.)."
    rcode = dlg.ShowModal()
    if rcode == wx.ID_OK:
        if bMulti and not bSave:
            filenames = dlg.GetPaths()
            save_start_path(RegistryKey, os.path.split(filenames[0])[0], AppName, bLocalMachine)
            ret = [rcode, filenames]
        else:
            filename = dlg.GetPath()
            save_start_path(RegistryKey, os.path.split(filename)[0], AppName, bLocalMachine)
            ret = [rcode, filename]
    else:
        ret = [rcode, None]
    if bReturnFileType:  # also return index of user-selected wildcard in 'Save of type' list
        ret.append(dlg.GetFilterIndex())
    return ret


def GetDirFromUserQT(parent, RegistryKey=None, DefaultVal=".", Title="Browse for folder", Message="",
                     AppName="\\Pydro", bLocalMachine=0):
    '''Pops up a dialog to get a directory from the user.
       Returns a two-item list [return code, pathname (or None)]
    '''

    startpath = get_start_path(RegistryKey, DefaultVal, AppName, bLocalMachine)

    pathname = QFileDialog.getExistingDirectory(parent, Title, startpath)
    if pathname:
        save_start_path(RegistryKey, pathname, AppName, bLocalMachine)
        ret = [pathname, pathname]
    else:
        ret = [pathname, ""]
    return ret


def GetFilenameFromUserQT(parent, bSave=1, RegistryKey=None, DefaultVal=".", Title="Choose a path/filename", DefaultFile="", fFilter="All Files (*.*)",
                          AppName="\\Pydro", bLocalMachine=0, bMulti=0, bReturnFileType=0):
    startpath = get_start_path(RegistryKey, DefaultVal, AppName, bLocalMachine)
    if DefaultFile:
        if startpath == '.':
            startpath = os.path.join(r'C:\\', DefaultFile)
        else:
            startpath = os.path.join(startpath, DefaultFile)
    if bSave:
        filename, ffilter = QFileDialog.getSaveFileName(parent, Title, startpath, fFilter)
        rcode = bool(filename)
    elif bMulti:
        filename, ffilter = QFileDialog.getOpenFileNames(parent, Title, startpath, fFilter)
        rcode = bool(filename)
    else:
        filename, ffilter = QFileDialog.getOpenFileName(parent, Title, startpath, fFilter)
        rcode = bool(filename)

    if rcode:
        if bMulti and not bSave:
            save_start_path(RegistryKey, os.path.split(filename[0])[0], AppName, bLocalMachine)
            ret = [rcode, filename]
        else:
            save_start_path(RegistryKey, os.path.split(filename)[0], AppName, bLocalMachine)
            ret = [rcode, filename]
    else:
        ret = [rcode, filename]
    if bReturnFileType:  # also return index of user-selected wildcard in 'Save of type' list
        ret.append(ffilter)
    return ret

def uninitialized(*args, **kwargs):
    raise RuntimeError("GUI library not initialized")

GetDirFromUser = uninitialized
GetFilenameFromUser = uninitialized

def use_wx():
    global GetDirFromUser, GetFilenameFromUser
    GetDirFromUser = GetDirFromUserWX
    GetFilenameFromUser = GetFilenameFromUserWX

def use_qt():
    global GetDirFromUser, GetFilenameFromUser
    GetDirFromUser = GetDirFromUserQT
    GetFilenameFromUser = GetFilenameFromUserQT

if "wx" in sys.modules.keys():
    import wx
    use_wx()
elif "PySide6" in sys.modules.keys():
    from PySide6.QtWidgets import QFileDialog
    use_qt()
elif "PySide2" in sys.modules.keys():
    from PySide2.QtWidgets import QFileDialog
    use_qt()
elif "PyQt5" in sys.modules.keys():
    from PyQt5.QtWidgets import QFileDialog
    use_qt()
else:
    print("No GUI library found, import PySide6, PySide2, PyQt5 or wx before RegistryHelpers", file=sys.stderr)

