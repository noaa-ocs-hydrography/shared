import os
import distutils.sysconfig

try:
    from win32api import GetShortPathName as get_short_path_name
except ImportError:
    pass  # fail silently on linux

import HSTB
try:
    from HSTB import Docs
except ImportError:
    pass


def path_to_HSTB(*paths):
    # for f in inspect.stack():
    #     print('-', inspect.getframeinfo(f[0]))
    print("Warning -- path_to_HSTB is not reliable in 3.8 with the move to git repo and namespaces")
    return os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(__file__)), *paths))


def path_to_NOAA(*paths):
    return os.path.normpath(os.path.join(path_to_HSTB(), "..\\..\\..\\..\\..", *paths))


def path_to_root_env(*paths):
    return os.path.normpath(os.path.join(path_to_NOAA(), "..", *paths))


def path_to_supplementals(*paths):
    return os.path.normpath(os.path.join(path_to_root_env(), 'supplementals', *paths))


def path_to_conda(*paths):
    return os.path.normpath(os.path.join(path_to_root_env(), "scripts", *paths))


def path_to_envs(*paths):
    return os.path.normpath(os.path.join(path_to_root_env(), "envs", *paths))


def path_to_NOAA_site_packages(*paths):
    return os.path.normpath(os.path.join(path_to_NOAA(), "site-packages", *paths))


def path_to_resource(*paths):
    return os.path.normpath(os.path.join(os.path.dirname(__file__), *paths))


def PathToResource(*paths):
    return path_to_resource(*paths)

# @todo remove these Docs functions and leave it to the individual apps to specify the locations
def path_to_docs(*paths):
    return os.path.normpath(os.path.join(os.path.dirname(Docs.__file__), *paths))


# @todo remove these Docs functions and leave it to the individual apps to specify the locations
def PathToDocs(*paths):
    """ returns full path to the Docs directory and appends any subdirectories specified

    Parameters
    ----------
    paths
        subdirectories to add to the docs path

    Returns
    -------

    """
    return path_to_docs(*paths)


def path_to_html(*paths):
    return os.path.normpath(os.path.join(path_to_docs(), "html", *paths))


_activate = path_to_conda("activate")  # e.g.  c:\pydroxl_19\scripts\activate
try:
    pathToActivate = get_short_path_name(_activate)
except:
    pass
_pythonpath = os.path.dirname(os.path.dirname(distutils.sysconfig.get_python_lib()))  # python_dir/lib/site-packages then back to python_dir
_default_env = "Pydro367"


def create_env_cmd(env=_default_env, persistant=False):
    return " ".join(create_env_cmd_list(env, persistant))


def create_env_cmd_list(env=_default_env, persistant=False):
    """
    Get a parameter list compatible with subprocess for running an environment.
    User can then append the commands to run in a console to the end of the returned list.
    The returned list will:
      start with cmd.exe (start a console)
      set XXX (set or clear some windows environment variables, like PYTHONPATH and TK that can interfere if carried over)
      end with && so additional commands can be appended (for convenience)

    Parameters
    ----------
    env
        Environment to activate as string -- Pydro27 or Pydro367
    persistant
        Keep the console open after the command is run --
        True keeps the console open (/K) and False has the console close (/C)

    Returns
    -------
        list of arguments that can be passed to subprocess or joined using a space
        e.g.   " ".join(args)

    """
    # run shell (/K: leave open (debugging), /C close the shell)
    p_switch = "/K" if persistant else "/C"
    command = ["cmd.exe", p_switch,
               "set", "pythonpath=&&",
               "set", "TCL_LIBRARY=&&", "set", "TIX_LIBRARY=&&", "set", "TK_LIBRARY=&&",
               ]
    if env:
        command += [_activate, env, "&&"]
    return command
