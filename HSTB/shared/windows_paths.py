import os
import ctypes
from ctypes import wintypes

def get_short_path_name(long_name):
    """
    Gets the short path name of a given long path.
    http://stackoverflow.com/a/23598461/200291
    """
    pth = os.path.abspath(long_name)  # converts "." and ".."
    _GetShortPathNameW = ctypes.windll.kernel32.GetShortPathNameW
    _GetShortPathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
    _GetShortPathNameW.restype = wintypes.DWORD
    output_buf_size = 0
    while True:
        output_buf = ctypes.create_unicode_buffer(output_buf_size)
        needed = _GetShortPathNameW(pth, output_buf, output_buf_size)
        if output_buf_size >= needed:
            if needed == 0:
                return long_name
            return str(output_buf.value)
        else:
            output_buf_size = needed

def get_long_path_name(short_name):
    """Get a long name from a short name on windows
    https://stackoverflow.com/questions/11420689/how-to-get-long-file-system-path-from-python-on-windows
    """
    pth = os.path.abspath(short_name)  # converts "." and ".."
    get_long_path_name = ctypes.windll.kernel32.GetLongPathNameW
    get_long_path_name.restype = wintypes.DWORD
    get_long_path_name.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
    output_buf_size = 0
    while True:
        output_buf = ctypes.create_unicode_buffer(output_buf_size)
        needed = get_long_path_name(pth, output_buf, output_buf_size)
        if output_buf_size >= needed:
            if needed == 0:
                return short_name
            return str(output_buf.value)
        else:
            output_buf_size = needed
