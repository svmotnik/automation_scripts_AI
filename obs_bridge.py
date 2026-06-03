import obspython as obs
import subprocess
import os

def launch_gui(*args):
    # Sprawdzamy czy proces już żyje, aby nie otwierać 10 okien
    subprocess.Popen(["python3", os.path.expanduser("~/obs_scripts/bug_reporter_gui.py")])

def script_load(settings):
    obs.obs_hotkey_register_frontend("open_bug_gui", "Bug Reporter", launch_gui)

