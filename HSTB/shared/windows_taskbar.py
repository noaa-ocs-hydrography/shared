import sys
import ctypes

def separate_taskbar(version="", name=None):
    """ This function will rename the app user model id which controls if the taskbar icon is grouped.
    All Python.exe runs were being grouped together in the taskbar, this will separate them out if called.
    The same script being run multiple times will be grouped together in the taskbar.

    Use the version in case you want different versions of the same script name to be separated.

    Override the name if you want to use a different name than the script name, otherwise the sys.argv will be used.

    Applicable to windows only.
    """
    try:
        if name is None:
            name = sys.argv[0]
            if name == "-m":
                name = sys.argv[1]

        myappid = f'pydro.{name}{version}'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except:
        pass
