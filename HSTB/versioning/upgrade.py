from __future__ import print_function
# example format   "#" are comment lines
# Line1: Version (Constants.GetVersion()) it applys to (comma separated for multiple versions to update)
# Line2: Version it results in after application
# Line3: Size in Kb (comma separated for multiple versions to update -- must match length of versions above)
# Line4: URL for SVN switch
# Line5: Path to apply SVN switch to (".." gets to the pythonXX folder as the path is relative to the pydro/source directory)
# Line 6: Recursive switch (boolean 1 or 0)
#
# Sample to recursively update the site-packages
#
# 1.1 r2345
# 1.2 r2366
# 34
# https://svn.pydro.com/pydro/tags/2.0
# ../Lib/Site-packages
# 1


import os
import distutils.sysconfig
import distutils.dir_util
import subprocess
import shutil
import hashlib
import tempfile
import pprint
import traceback

try:
    import ProcessedUpdates
    processed_updates = ProcessedUpdates.processed
except:
    processed_updates = {}

import HSTB.resources

path_to_slik = HSTB.resources.path_to_NOAA_site_packages("SlikSvn\\bin\\svn.exe")

if not os.path.exists(path_to_slik):
    print("Couldn't find a svn.exe for subversion client\n")
# else:
#     print("using svn at ", path_to_slik)

PathToSitePkgs = distutils.sysconfig.get_python_lib()
nfiles = 0


def RunCommand(cmd):
    '''Run the passed in command and return a tuple of the std_out and std_err

    subprocess.Popen is used and the stderr and stdout are sent to temporary files to avoid blocking the program,
    the temporary files are then read and passed back before being removed.
    '''
    std_out = tempfile.TemporaryFile()  # deleted on exit from function
    std_err = tempfile.TemporaryFile()
    try:
        p = subprocess.Popen(cmd, stderr=std_err, stdout=std_out)  # , stdin=std_in
    except WindowsError:  # this happens when running from PythonW.exe
        p = subprocess.Popen(cmd, stderr=std_err, stdout=std_out, stdin=subprocess.PIPE)  # , stdin=std_in
    p.wait()  # let the process finish
    std_out.seek(0)
    std_err.seek(0)
    out = std_out.read()
    err = std_err.read()
    try:
        out = out.decode("utf-8")  # converts from bytes in python 3.x
    except AttributeError:
        pass
    try:
        err = err.decode("utf-8")  # converts from bytes in python 3.x
    except AttributeError:
        pass

    return out, err


def md5(fname):
    '''returns an MD5 hash if the file exists or None if the file doesn't exit (or is a directory name)'''
    hash = hashlib.md5()
    try:
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash.update(chunk)
        return hash.hexdigest()
    except IOError:
        return None
# >>> md5(r'C:\PydroTrunk\Python27_x64\Lib\site-packages\hdf_compass\array_model\model.py')
# '0cf8c0dd3d9cb93daba1890ec24528cc'
# >>> md5(r'C:\PydroTags\Pydro15_10_Installed\Lib\site-packages\hdf_compass\array_model\model.py')
# '2548d538404d5f9d3ba3bd88c0cbf3b1'


class SlikSVNClient:
    def __init__(self):

        self.userpass = "--no-auth-cache --username public --password c0ntract0r"

    def update(self, path, recurse=True):
        return RunCommand(" ".join(['"' + path_to_slik + '"',
                                    self.userpass,
                                    'update',
                                    '"' + path + '"',
                                    ]))

    def checkout(self, path, url, recurse=True):
        return RunCommand(" ".join(['"' + path_to_slik + '"',
                                    self.userpass,
                                    'checkout',
                                    '"' + url + '"',
                                    '"' + path + '"',
                                    ]))

    def export(self, path, url, recurse=True):
        # use --force so it will export directly to the directory supplied
        return RunCommand(" ".join(['"' + path_to_slik + '"',
                                    self.userpass,
                                    '--force export',
                                    '"' + url + '"',
                                    '"' + path + '"',
                                    ]))

    def switch(self, path, url, recurse=True):
        return RunCommand(" ".join(['"' + path_to_slik + '"',
                                    self.userpass,
                                    'switch',
                                    '"' + url + '"',
                                    '"' + path + '"',
                                    ]))

    def info(self, path):
        return RunCommand(" ".join(['"' + path_to_slik + '"',
                                    'info',
                                    '"' + path + '"',
                                    ]))

    def cleanup(self, path):
        return RunCommand(" ".join(['"' + path_to_slik + '"',
                                    'cleanup',
                                    '"' + path + '"',
                                    ]))

    def exclude(self, path):
        '''
        #REMOVE THE DIRECTORY
        C:\PydroTrunk\Python27_x64\Lib\site-packages\hydroffice\sarscan>..\..\HSTPBin\SlikSvn\svn update docs --set-depth exclude
        D    docs

        #CHECK THE STATUS AND SEE IF INSTALLED
        C:\PydroTrunk\Python27_x64\Lib\site-packages\hydroffice\sarscan>..\..\HSTPBin\SlikSvn\svn info docs
        Path: docs
        Working Copy Root Path: C:\PydroTrunk
        URL: http://205.156.4.93/svn/trunk/Python27_x64/Lib/site-packages/hydroffice/sarscan/docs
        Relative URL: ^/trunk/Python27_x64/Lib/site-packages/hydroffice/sarscan/docs
        Repository Root: http://205.156.4.93/svn
        Repository UUID: 78d86a9e-7f17-0410-ab43-c37b7e518f2b
        Revision: 5249
        Node Kind: directory
        Schedule: normal
        Depth: exclude

        #RESTORE THE DIRECTORY -- THIS WORKS WITHOUT INTERNET CONNECTION AS IT COMES FROM THE LOCAL .SVN CACHE
        C:\PydroTrunk\Python27_x64\Lib\site-packages\hydroffice\sarscan>..\..\HSTPBin\SlikSvn\svn update docs
        Updating 'docs':
        A    docs
        A    docs\manual.pdf
        A    docs\manual.docx
        Updated to revision 5249.
        '''
        return RunCommand(" ".join(['"' + path_to_slik + '"',
                                    self.userpass,
                                    'update --set-depth exclude',
                                    '"' + path + '"',
                                    ]))

    def unexclude(self, path):
        ''' This update on a directory removes the 'exclude' depth -- see exclude() docs
        '''
        return RunCommand(" ".join(['"' + path_to_slik + '"',
                                    self.userpass,
                                    'update',
                                    '"' + path + '"',
                                    ]))

    def revert(self, path):
        ''' if a file was deleted or has local changes this will restore the server's version to the local disk
        '''
        return RunCommand(" ".join(['"' + path_to_slik + '"',
                                    self.userpass,
                                    'revert',
                                    '"' + path + '"',
                                    ]))

    def isExcluded(self, path):
        info, _err = RunCommand(" ".join(['"' + path_to_slik + '"',
                                          'info',
                                          '"' + path + '"',
                                          ]))

        excluded = False
        for l in info.splitlines():
            if "Depth: exclude" in l:
                excluded = True
        return excluded

    def getRevision(self, path=None):
        if not path:
            path = path_to_slik
        info, err = RunCommand(" ".join(['"' + path_to_slik + '"',
                                         'info',
                                         '"' + path + '"',
                                         ]))
        if err:
            print("Error while running", " ".join(['"' + path_to_slik + '"', 'info', '"' + path + '"']))
            print(info)
            print(err)
            raise Exception("Failed to get svn info")
        else:
            for l in info.splitlines():
                if l.startswith("Revision:"):
                    PydroRev = "r" + l[10:]
                if l.startswith("Last Changed Date:"):
                    PydroRevTime = l[19:]
                if l.startswith("URL:"):
                    PydroURL = l[5:]
            # print PydroRev
            # print PydroRevTime
            # print PydroURL
            return PydroRev, PydroRevTime, PydroURL

# svn.update($local_folder, depth=pysvn.depth.infinity, depth_is_sticky=True)

## @todo I think this is deprecated -- delete it soon
# def Download(svn_url='', path='..', recurse=1):
#     '''if svn_url evaluates to bool False then it performs an update otherwise switch.
#     '''
#     # client=MakePydroSvnClient()
#     client = SlikSVNClient()
#     recurse = bool(recurse)
#     try:
#         # check for locked files -- python25 shoudl show most python programs, HydroMi in case of Mapinfo, PeekXTF to make sure there isn't a different Python install using our code
#         for fname in (  # '/../../python27.dll', '/../../python.exe',
#             '/HSTPBin/MidTierPeek70.pyd', '/HSTPBin/PeekXTF70.pyd',
#                 '/HSTP/Pydro/Hydro_MI.exe', '/HSTP/Pydro/Hydro_MI.MBX'):
#             filename = pkg_dir + "/" + fname
#             if os.path.exists(filename):
#                 f = open(filename, 'a')  # is the file locked so we can't change it?
#                 f.close()
#             # else: print filename, "doesn't exist"
#     except:
#         traceback.print_exc()
#         print('!*' * 40)
#         print()
#         print("There is a python/Pydro/HydroMI program open -- can not perform upgrade until all Python programs are closed")
#         print()
#         print('!*' * 40)
#         return 0
#
#     try:
#         global nfiles
#         nfiles = 0
#         # client.cleanup(path)
#
#         if not svn_url:
#             if 0:  # moved this into the RunProg batch file  -- That way we can update python too.
#                 print("Updating", path)
#                 client.update(path, recurse)
#         else:
#             # Got error on download when pydro.com and www.pydro.com didn't match so let's try keeping the url before the pydro.com
#             #
#             # Traceback (most recent call last):
#             # File "upgrade.py", line 58, in Download
#             #   else: client.switch(path, svn_url)
#             # ClientError:  ("'http://www.pydro.com/svn/tags/Release_8_10_r2515'\nis not the sa
#             # me repository as'http://pydro.com/svn'", [("'http://www.pydro.com/svn/tags/Rel
#             # ease_8_10_r2515'\nis not the same repository as\n'http://pydro.com/svn'", 155025
#             # cur_url = client.info(path)['repos']
#             # cur_url = client.info(path)
#             # print "current url:", cur_url
#             print("switching to:", svn_url)
#             # switch_url = cur_url[:cur_url.find('pydro')]+svn_url[svn_url.find('pydro'):]
#             switch_url = svn_url
#             print("Switching (recursively?)", bool(recurse), path)
#             print("To", switch_url)
#             client.switch(path, switch_url, recurse)
#         return -1  # finished successfully
#     except:
#         traceback.print_exc()
#         # client.callback_notify = exception_notify
#         try:
#             print("Trying to cleanup")
#             client.cleanup(path)
#             print("Finished cleanup - please run the program again and contact HSTP if there are continued problems")
#         except:
#             traceback.print_exc()
#             print()
#             print('Failed cleanup - please run the program again.  Depending on the error a uninstall/delete and re-install mey be required.\nContact HSTP with the messages in the console.')
#             pass
#         # except pysvn.ClientError, e:
#         #    try:
#         #        msg = e.args[1][2][0]
#         #        print msg
#         #        if "is not under version control" in msg:
#         #            fname = msg[1:msg.find("'", 2)]
#         #            print 'remove', fname
#         #            os.remove(fname)
#         #    except:
#         #        traceback.print_exc()
#         #    print '**************'
#         #    print e.args[0]
#         #    print '**************'
#         #    print e.args[1]
#         #    print '**************'
#         return nfiles


def UpdateDirectory(checkout_url, path_to_update):
    # get the current tag url
    # svn export the package to a temporary directory (so it doesn't have the .svn folder)
    bSuccess = False
    svn = SlikSVNClient()
    export_dir = tempfile.mkdtemp('', "PydroUpdate_")
    out, err = svn.export(export_dir, checkout_url)
    # if it seems to have finished downloading then
    if "Exported revision" in out:
        # rename the old directory (if it existed)
        basepath, directory = os.path.split(path_to_update)
        updatingExistingData = os.path.exists(path_to_update)
        old_data_path = tempfile.mkdtemp('_old', directory + "_", basepath)  # make a directory to move the existing files into
        try:
            # print "move old data if exists", os.path.exists(path_to_update)
            if updatingExistingData:
                shutil.move(path_to_update, old_data_path)
            try:
                # move the newly downloaded directory into the sitepackages
                # print "moving exported SVN", export_dir, path_to_update
                shutil.move(export_dir, path_to_update)
                bSuccess = True
            except:
                shutil.rmtree(path_to_update)
                # raise an exception so that the old data will be replaced back
                raise Exception("Failed to move the downloaded files into the new directory")
        except:
            # failed to move the old data, put it back -- it may have been in use.
            # print os.path.join(old_data_path,directory), path_to_update
            if updatingExistingData:
                distutils.dir_util.copy_tree(os.path.join(old_data_path, directory), path_to_update, update=True)
        # delete the old/renamed directory
        if updatingExistingData:
            shutil.rmtree(old_data_path, True)  # ignore errors on deletion
    shutil.rmtree(export_dir, True)  # ignore errors on deletion
    return bSuccess


class SitePackageInstructions:
    def __init__(self, site_package):
        self.site_package = site_package

    def DoDownload(self):
        '''Default download operation is to download from the new url and place it in place of the path_to_update.
        Derive from the class to change the behavior
        '''
        return self.UpdateSitePackage()

    def UpdateSitePackage(self):
        hstp_url = SlikSVNClient().getRevision()[2]
        site_package_url = os.path.split(hstp_url)[0]
        update_package_url = site_package_url + "/" + self.site_package
        return UpdateDirectory(update_package_url, os.path.join(PathToSitePkgs, self.site_package))

    def __repr__(self):
        return "Update instructions for " + str(self.site_package)


class Update:
    def __init__(self, file_to_check, hash_to_match, instructions):
        self.file_to_check = file_to_check
        self.hash_to_match = hash_to_match
        self.instructions = instructions

    def IsDone(self):
        try:
            return processed_updates[self.hash_to_match] == self.file_to_check
        except KeyError:
            return False

    def AlreadyUpdated(self):
        return md5(self.file_to_check) == self.hash_to_match

    def DoUpdate(self):
        bUpdated = False
        if not self.IsDone() and not self.AlreadyUpdated():
            bUpdated = self.instructions.DoDownload()
        return bUpdated

    def __repr__(self):
        return str(self.instructions) + " using hash " + self.hash_to_match


if __name__ == '__main__':
    try:  # major update -- svn switch
        batch = open('update.txt', 'r')
    except:  # minor updates -- updates and now site-packages to update also.
        # This is now in the runprog.bat calling sliksvn on the entire python directory structure.

        # print "Checking for minor Pydro updates..."
        # Download("", "..", True) #update the lib/sitepackages/HSTP directory and everything inside it.
        # print "Checking for HydrOffice updates"
        # Download("", "..\\..\\hydroffice", True) #update the lib/sitepackages/\hydroffice directory and everything inside it.

        hdf_compass_instr = SitePackageInstructions("hdf_compass")
        hdf_compass_update = Update(os.path.join(PathToSitePkgs, r'hdf_compass\array_model\model.py'), '2548d538404d5f9d3ba3bd88c0cbf3b1', hdf_compass_instr)

        gsw_compass_instr = SitePackageInstructions("gsw")
        gsw_compass_update = Update(os.path.join(PathToSitePkgs, r'gsw\utilities\utilities.py'), '8da0e348595f293be0ed5841de7b2659', gsw_compass_instr)

        upgrades = [hdf_compass_update,
                    gsw_compass_update,
                    ]
        # print "already done", processed_updates
        bUpdateApplied = False
        for u in upgrades:
            # print u.DoUpdate(), u.file_to_check
            # print md5(u.file_to_check),u.hash_to_match, u.AlreadyUpdated()
            if u.DoUpdate():
                processed_updates[u.hash_to_match] = u.file_to_check
                print("Processed", u)
                bUpdateApplied = True
        # write out the updated list
        if bUpdateApplied:
            fil = open("ProcessedUpdates.py", 'w+')
            fil.write("processed=")
            p = pprint.pformat(processed_updates, width=500, indent=4)
            fil.write(p)

        exit(0)
    prog = int(batch.readline().strip())
    up_to_ver = batch.readline().strip()
    svn_url = batch.readline().strip()
    local_dir = batch.readline().strip()
    recurse = batch.readline().strip()
    moreUpdates = batch.readlines()
    batch.close()
    nf = Download(svn_url, local_dir, int(recurse))
    if nf < 0:  # success -- remove the cookie file and return success
        os.remove('update.txt')
        if len(moreUpdates) > 4:  # another update to process
            batch = open('update.txt', 'wb+')
            batch.writelines(moreUpdates)
            exit(2)
        else:  # finished
            exit(0)

    elif nf > 0:  # failed after partial update - leave the file inplace showing progress
        batch = open('update.txt', 'wb+')
        for l in (str(nf + prog), up_to_ver, svn_url, local_dir, recurse):
            batch.write('%s\n' % l)
        batch.writelines(moreUpdates)
        batch.close()
    exit(1)
