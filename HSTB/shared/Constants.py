from __future__ import with_statement, print_function
'''
Constants.py contains values and names that should be used across any python modules.  It contains
the major version number for Pydro installations.  Further it has datum names, units conversions and
other miscellaneous constants for use with other code (like ADO).

'''

from math import pi
try:
    import numpy  # for infinity
except:
    print("Failed to import numpy for infinity")
import math
import sys
import time
import re

try:
    from HSTB.shared.HSTPSettings import *  # @todo remove code relying on this so that importing Constants doesn't load registryHelpers
except:
    print("HSTPSettings didn't import -- some functions will not work!")

datumKeys = ['MHHW', 'MHW', 'MLW', 'MLLW', 'MSL', 'MTL', 'DTL', 'NGVD', 'NAVD']
ENC_CONTACT_STRING = " ENC_GPs - "
XREFDELIM = '*&*'
StdKeywords = ('Unassigned', 'Assigned', 'For Info Only', 'Bottom Sample', 'ATON', 'AWOIS', 'Maritime Boundary', 'CEF')  # note: 'AWOIS' to handle those [rogue] AWOIS-related items that come in to PSS in non-standard way
DRKeywords = {"DR via FPM Pydro Flags": ('DR_Charted', 'DR_UnCharted', 'DR_AWOIS', 'DR_DToN'),  # 1:1 with DRChapterNames, below
              "DR via HSSD Extended S-57 Attributes": ('S57DR_Charted', 'S57DR_UnCharted', 'S57DR_AWOIS', 'S57DR_DToN', 'S57DR_AToN', 'S57DR_NotAddressed'),
              "HCell Feature Report": ('HCellFR_AWOIS', 'HCellFR_DToN', 'HCellFR_MaritimeBoundary', 'HCellFR_Wrecks')}
DR_AWOISchapName, DR_DTONchapName = "AWOIS Features", "Dangers To Navigation"  # reserved strings used elsewhere in code
DRChapterNames = {"DR via FPM Pydro Flags": ("Charted Features", "New Features", DR_AWOISchapName, DR_DTONchapName),  # 1:1 with DRKeywords, above
                  "DR via HSSD Extended S-57 Attributes": ("Charted Features", "New Features", DR_AWOISchapName, DR_DTONchapName, "Aids to Navigation", "Not Addressed Features"),
                  "HCell Feature Report": (DR_AWOISchapName, DR_DTONchapName, "Maritime Boundary Features", "Wreck Features")}

illegalcharsXML = re.compile(u'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]')


def stripXMLillegalchars(txt):
    return illegalcharsXML.subn('', txt)[0]


# Vessel utilization statistics; naming per SurveyStatistics.xsd StatsLNMType TableType elements (+ suffix "_LNMlogic")
# SB+MB XL combined:
XL_MBES_SBES_LNMlogic = "bool(set([mode.strip() for mode in sMode.split(',')]).intersection(set(['Interferometric', 'Multibeam', 'SingleBeam']))) and sType=='Crossline'"
# SB only:
MS_SBES_LNMlogic = "sMode in ('SingleBeam', 'Shoreline, SingleBeam') and sType in ('Mainscheme', 'Development')"
# MB only:
MS_MBES_LNMlogic = "(sMode.find('Multibeam')>=0 or sMode.find('Interferometric')>=0) and sMode.find('SingleBeam')<0 and sMode.find('SideScanSonar')<0 and sType in ('Mainscheme', 'Development')"
# SS only:
MS_SSS_LNMlogic = "sMode.find('SideScanSonar')>=0 and sMode.find('SingleBeam')<0 and not (sMode.find('Multibeam')>=0 or sMode.find('Interferometric')>=0) and sType in ('Mainscheme', 'Development')"
# SB+SS combo
MS_SBES_SSS_LNMlogic = "sMode.find('SingleBeam')>=0 and sMode.find('SideScanSonar')>=0 and not (sMode.find('Multibeam')>=0 or sMode.find('Interferometric')>=0) and sType in ('Mainscheme', 'Development')"
# MB+SB combo
MS_SBES_MBES_LNMlogic = "sMode.find('SingleBeam')>=0 and sMode.find('SideScanSonar')<0 and (sMode.find('Multibeam')>=0 or sMode.find('Interferometric')>=0) and sType in ('Mainscheme', 'Development')"
# MB+SS combo
MS_MBES_SSS_LNMlogic = "sMode.find('SideScanSonar')>=0 and sMode.find('SingleBeam')<0 and (sMode.find('Multibeam')>=0 or sMode.find('Interferometric')>=0) and sType in ('Mainscheme', 'Development')"
# Unaccounted: <total - count>
# e.g., MB+SS+SB, Shoreline (alone) + any Type, UnclassifiedMode or UnclassifiedType, SideScanSonar + XL
MS_lidar_LNMlogic = "False"
XL_lidar_LNMlogic = "False"

# regard PyMidTierPeek CSurveyLineBase int m_nClassification values as a binary mask to encode flags for (mixed) Mode and Type states
# (assuming sizeof(type(m_nClassification))==4 bytes)
# old "indexes" -1:'Unclassified',0:'MainScheme',1:'CheckLine',2:'Other'; mapped to new encoding in PyPeekXTF DLL
# --todo in DLL:  Caris line (Type only, not Mode) classification bits ([SSS]Navigation summary status word) defined in HIPSio navigation.h, copied below:
#NAV_CHECK_LINE_MASK ((long(1))<<28)
#NAV_PATCH_TEST_LINE_MASK ((long(1))<<27)
#NAV_SHOAL_EXAMINATION_LINE_MASK ((long(1))<<26)
#NAV_TRACK_LINE_MASK ((long(1))<<25)
LineClassModeFromMask = {int(1) << 0: 'UnclassifiedMode', int(1) << 1: 'Multibeam', int(1) << 2: 'SingleBeam', int(1) << 3: 'SideScanSonar', int(1) << 4: 'Shoreline', int(1) << 5: 'Interferometric'}  # bits 0-7 for "mode", nominally
LineClassTypeFromMask = {int(1) << 8: 'UnclassifiedType', int(1) << 9: 'Mainscheme', int(1) << 10: 'Crossline', int(1) << 11: 'Development', int(1) << 12: 'Other'}  # bits 8-15 for "type", nominally
LineClassTypeColorFromMask = {int(1) << 8: 0x000000, int(1) << 9: 0x0000ff, int(1) << 10: 0x00ff00, int(1) << 11: 0xff0000, int(1) << 12: 0x008080}
LineClassNameFromMaskInclCaris = {int(1) << 16: 'UnclassifiedCaris', int(1) << 17: 'CheckLineCaris', int(1) << 18: 'PatchTestLineCaris', int(1) << 19: 'ShoalExamineCaris', int(1) << 20: 'TrackLineCaris'}  # bits 16-23 for Caris, nominally


def GetLineClassColor(lineClassMask): return LineClassTypeColorFromMask.get(lineClassMask & 0x00ff00, 0x000000)  # lookup from truncated-to-type mask (middle byte)--assuming non-combo types possible


LineClassTypeFromMaskInclCaris = {}
LineClassTypeFromMaskInclCaris.update(LineClassTypeFromMask)
LineClassTypeFromMaskInclCaris.update(LineClassNameFromMaskInclCaris)
LineClassNameFromMask = {}
LineClassNameFromMask.update(LineClassModeFromMask)
LineClassNameFromMask.update(LineClassTypeFromMask)
LineClassNameFromMaskInclCaris.update(LineClassNameFromMask)
LineClassMaskFromName = dict(map(lambda lineClassItems: (lineClassItems[1], lineClassItems[0]), LineClassNameFromMask.items()))
LineClassMaskFromNameInclCaris = dict(map(lambda lineClassItems: (lineClassItems[1], lineClassItems[0]), LineClassNameFromMaskInclCaris.items()))
DefaultModeName, DefaultTypeName = 'UnclassifiedMode', 'UnclassifiedType'
DefaultModeMask, DefaultTypeMask = LineClassMaskFromName[DefaultModeName], LineClassMaskFromName[DefaultTypeName]
LineTypeNameCaris2Pydro = {'TrackLineCaris': 'Mainscheme', 'CheckLineCaris': 'Crossline', 'ShoalExamineCaris': 'Development', 'PatchTestLineCaris': 'Other'}  # todo: in PyMidTierPeek map HDCS [SSS]Navigation line class
LineTypeNameOld2New = {'MainScheme': 'Mainscheme', 'CheckLine': 'Crossline', 'Other': 'Other', 'Unclassified': 'UnclassifiedType'}  # this is implemented in the PyMidTierPeek DLL


def GetLineClassMask(lineModeNames, lineTypeNames, bIgnoreCaris=True):
    # assumption: a priori validation of line[Mode,Type]Names, s.t. classification is not both 'Unclassified' and other value(s)
    if bIgnoreCaris:
        maskFromName = LineClassMaskFromName
    else:
        maskFromName = LineClassMaskFromNameInclCaris
    modeMask, typeMask = int(0), int(0)
    try:
        for lineModeName in lineModeNames:
            modeMask |= maskFromName[lineModeName]
    except KeyError:
        modeMask = DefaultModeMask
    try:
        for lineTypeName in lineTypeNames:
            typeMask |= maskFromName[lineTypeName]
    except KeyError:
        typeMask = DefaultTypeMask
    if modeMask == int(0):
        modeMask = DefaultModeMask
    if typeMask == int(0):
        typeMask = DefaultTypeMask
    return modeMask | typeMask


def IsFSObjectOfLineClass(fsobj, lineClassName):
    classMask = fsobj.GetClassification()
    try:
        bRet = classMask & LineClassMaskFromNameInclCaris(lineClassName)
    except:
        bRet = False
    return bRet


def GetLineClassNames(lineClassMask, bIgnoreCaris=True):
    if bIgnoreCaris:
        typeMaskFromName = LineClassTypeFromMask
    else:
        typeMaskFromName = LineClassTypeFromMaskInclCaris
    lineModeNames, lineTypeNames = [], []
    lineModeNames = [choiceName for choiceMask, choiceName in LineClassModeFromMask.iteritems() if choiceMask & lineClassMask]
    lineTypeNames = [choiceName for choiceMask, choiceName in typeMaskFromName.iteritems() if choiceMask & lineClassMask]
    if not lineModeNames:
        lineModeNames = [DefaultModeName]
    if not lineTypeNames:
        lineTypeNames = [DefaultTypeName]
    lineModeNames.sort()  # e.g., to match sorted LineInfoDlg LineInfoCategorizationDlg names
    lineTypeNames.sort()
    return lineModeNames, lineTypeNames
# Replace [Constants.]'[Line]ClassIndex' with [Constants.]'GetLineClassMask
# def ClassIndex(value):
#    try:
#        ind=list(LineClasses).index(value)
#        if value=='Unclassified': ind=-1
#    except ValueError:
#        ind=-1
#    return ind


def PrimWithSecondaryAWOISAdvStr():
    #.strip() is TEMPORARY FIX FOR LEADING-SPACE BUG IN <ExcessLevel> ELEMENT
    execstr = """\
retval=(0,None,None)
xrf=MakeXRefString(cl,con)
correlating=GetAllCorrelatingContacts(cf,cl,con)
for f,tcl,tcn,txc in correlating:
    if IsAwois(tcn) and tcn.GetExcessLevel()[1]==xrf.strip():
        retval=(1,tcl,tcn)
        break
"""
    return execstr


def NavSampleRate():
    return 1.0  # one second nav used to pass into Douglas Peucker line simplification


def NavTolerance():
    return 5.0  # 5 meters tolerance on navigation


def PydroVersion():
    return '21.3'


def PydroTitleVersion():
    return PydroFullVersion()


def PydroVersionIsDev():
    is_dev = "/trunk/" in PydroSVN_URL().lower()
    return is_dev


def PydroVersionType():
    """ Return "Developer" or "Release" to indicate if the repository is from trunk or tag
    """
    install_type = "Developer" if PydroVersionIsDev() else "Release"
    return install_type


def PydroFullVersion():
    is_dev = " DEVELOPER " if PydroVersionIsDev() else ""
    return PydroVersion() + "(%s)" % PydroMinorVersion() + is_dev + UseDebug() * " dbg"


try:
    # check these on initial import as they could be updated in theory while the program is running
    from HSTB.versioning import GetSVN_Revision
    #changes = client.status(PathToSitePkgs+"/HSTP")
    #changed_files = [f.path for f in changes if f.text_status == pysvn.wc_status_kind.modified]
    PydroRev, PydroRevTime, PydroURL = GetSVN_Revision.CallGetRevision()
except:
    PydroRev, PydroRevTime, PydroURL = "Error determining revision", "Error determining revision time", "Error determining url"


def PydroMinorVersion():
    return PydroRev


def PydroMinorVersionTime():
    return PydroRevTime


def PydroSVN_URL():
    return PydroURL


def DEG2RAD():
    return 0.017453292519943295  # = pi/180.0


def RAD2DEG():
    return 57.295779513082323   # = 180.0/pi


def METERS2FEET():
    return 3.280839895013123    # = 1.0/0.3048


def METERS2FATH():
    return 0.5468066491688538   # = (1.0/0.3048)/6.0


def FEET2METERS():
    return 0.3048


def FATH2METERS():              # = 1.0/METERS2FATH()
    return 1.8288


unit_conversions = {
    'meters': {'meters': 1.0, 'fathoms': METERS2FATH(), 'feet': METERS2FEET()},
    'feet': {'meters': FEET2METERS(), 'fathoms': 1. / 6., 'feet': 1.0},
    'fathoms': {'meters': FATH2METERS(), 'fathoms': 1.0, 'feet': 6.0}
}


def INFINITY():
    return numpy.finfo(numpy.float_).max  # max value of the system's default float
#   Alternate code that runs on linux (or any IEEE 754 platform... not sure if it has any advantages)
#    if 'linux' in sys.platform:
#      return float('inf')


def VBESsoundspeed():
    return 1500.0


def NULLDEPTH():                # old school support
    return 99999.99


def UTC01011901to01011970():    # Python time module Epoch is 01/01/1970 00:00, XSE's is 01/01/1901 00:00
    return 2177452800.0


def UTCs80to01011901():         # XSE time datum is 01/01/1901 00:00, HDCS's is 01/01/1980 00:00
    return -2492985600.0


def PStack():  # print the call stack
    import traceback
    traceback.print_stack()


def callerFunc():
    try:
        raise Exception("arg")
    except:
        func = sys.exc_traceback.tb_frame.f_back.f_code.co_name
    return func

# Module: ADOConstants
# Author: Mayukh Bose
# Version: 0.0.1
# Purpose: To contain constant names for various ADO operations. Note that this is
#          not a comprehensive list of all constants.
# Modifications (push down list):
# 2004-February-15 - Released module to the public
#
# Copyright (c) 2004, Mayukh Bose
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:

#    Redistributions of source code must retain the above copyright notice, this list
# of conditions and the following disclaimer.
#    Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or other
# materials provided with the distribution.
#    Neither the name of Mayukh Bose nor the names of other contributors may be used to
# endorse or promote products derived from this software without specific prior written
# permission.
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
# OF SUCH DAMAGE.


#
# Data Type Constants
#

adEmpty = 0
adSmallInt = 2
adInteger = 3
adSingle = 4
adDouble = 5
adCurrency = 6
adDate = 7
adBSTR = 8
adIDispatch = 9
adError = 10
adBoolean = 11
adVariant = 12
adIUnknown = 13
adDecimal = 14
adTinyInt = 16
adUnsignedTinyInt = 17
adUnsignedSmallInt = 18
adUnsignedInt = 19
adBigInt = 20
adUnsignedBigInt = 21

adFileTime = 64
adGUID = 72

adBinary = 128
adChar = 129
adWChar = 130
adNumeric = 131
adUserDefined = 132
adDBDate = 133
adDBTime = 134
adDBTimeStamp = 135
adChapter = 136
adDBFileTime = 137
adPropVariant = 138
adVarNumeric = 139

adVarchar = 200
adVarChar = 200
adLongVarChar = 201
adVarWChar = 202
adLongVarWChar = 203
adVarBinary = 204
adLongVarBinary = 205


#
# Connection State Constants
#
adStateClosed = 0
adStateOpen = 1
adStateConnecting = 2
adStateExecuting = 4
adStateFetching = 8

#
# CursorType constants
#
adOpenUnspecified = -1
adOpenForwardOnly = 0
adOpenKeyset = 1
adOpenDynamic = 2
adOpenStatic = 3

#
# LockType constants
#
adLockUnspecified = -1
adLockReadOnly = 1
adLockPessimistic = 2
adLockOptimistic = 3
adLockBatchOptimistic = 4

#
# ExecuteOption constants
#
adOptionUnspecified = -1
adAsyncExecute = 16
adAsyncFetch = 32
adAsyncFetchNonBlocking = 64
adExecuteNoRecords = 128

#
# CursorLocation constants
#
adUseNone = 1
adUseServer = 2
adUseClient = 3
adUseClientBatch = 3

#
# ParameterDirection constants
#
adParamUnknown = 0
adParamInput = 1
adParamOutput = 2
adParamInputOutput = 3
adParamReturnValue = 4

#
# ParameterAttributes constants
#
adParamSigned = 16
adParamNullable = 64
adParamLong = 128

#
# CommandType constants
#
adCmdUnspecified = -1
adCmdText = 1
adCmdTable = 2
adCmdStoredProc = 4
adCmdUnknown = 8
adCmdFile = 256
adCmdTableDirect = 512

# (jlr) from http://www.a1vbcode.com/vbtip.asp?ID=161
# MS Access..............SQL Server........ADO Constant
# Yes/No.................Bit...............adBoolean
# Number(Byte)...........TinyInt...........adTinyInt
# Number(Integer)........SmallInt..........adSmallInt
# Number(Long Integer)...Int...............adInteger
# Number(Single).........Real..............adSingle
# Number(Double).........Float.............adDouble
# Currency...............Money.............adCurrency
#.......................Smallmoney........adCurrency
# Decimal/Numeric........Decimal...........adDecimal
#.......................Numeric...........adNumeric
# Date/Time..............Datetime..........adDate
#.......................Smalldatetime.....adDBDate
# AutoNumber.............Int...............adInteger
# Text(n)................Varchar(n)........adVarchar
#.......................Nvarchar(n).......adVarchar
# Memo...................Text..............adLongVarWChar
# OLE Object.............Image.............adLongVarBinary
# Replication ID.........Uniqueidentifier..adGUID
