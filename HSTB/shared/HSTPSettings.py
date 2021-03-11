from . import RegistryHelpers

def UseDebug():
    return RegistryHelpers.GetDWORDFromRegistry("debug", "HSTP", 0, bSilent=1)
def GetChartStyle():
    return RegistryHelpers.GetDWORDFromRegistry("WindowStyling", "BSB_ENC", 0, bSilent=1)
def SetChartStyle(val):
    return RegistryHelpers.SaveDWORDToRegistry("WindowStyling", "BSB_ENC", val)
def GetSplitterStyle():
    return RegistryHelpers.GetDWORDFromRegistry("WindowStyling", "Splitters", 1, bSilent=1)
def SetSplitterStyle(val):
    return RegistryHelpers.SaveDWORDToRegistry("WindowStyling", "Splitters", val)
def ShowTiming():
    return RegistryHelpers.GetDWORDFromRegistry("debug", "ShowTiming", 0, bSilent=1)

if 0 and UseDebug():
    import win32pdhutil
    import wmi
    if 0: #prints the free disk space, total size and % free of disk drives.
        try:
            c = wmi.WMI()
            for disk in c.Win32_LogicalDisk (DriveType=3):
                print(disk.Caption, "%.1fGb free %.1fGb avail -- %0.2f%% free" % ((long(disk.FreeSpace))*1.0e-9, (long(disk.Size))*1.0e-9, (100.0 * long (disk.FreeSpace) / long (disk.Size))))
        except: pass

    import win32process
    current_id = win32process.GetCurrentProcessId ()
    def wmi_mem():
        c = wmi.WMI (find_classes=False)
        for process in c.Win32_Process (['WorkingSetSize'], Handle=current_id):
            return process.WorkingSetSize
    last_mem=win32pdhutil.FindPerformanceAttributesByName("python", counter="Virtual Bytes")
    last_wmi=wmi_mem()
    def mem(t='', p=1):
        global last_mem
        last_mem=win32pdhutil.FindPerformanceAttributesByName("python", counter="Virtual Bytes")
        if p: print(t,last_mem, '%.3fMb'%(int(long(wmi_mem())//1024.0)/1000.))
        return last_mem
    def dmem(t='', p=1):
        lmem=last_mem
        nmem=mem(p=0)
        ret=[(nmem[n]-lmem[n])*1.0e-3 for n in range(min(len(lmem), len(nmem)))]
        if p: print(t,ret, '%.3fMb'%(int(long(wmi_mem())//1024.0)/1000.))
        return ret
else:
    def mem(p=0, t=''): pass
    def dmem(p=0, t=''):pass
