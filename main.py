# todo:
# - layout scheme for elements
# - redirect output from stdout of subprocess to logger (properly, 'external'-tag-wise)
# - refactor main.py

import subprocess
import os

from gui import Window, tk, ttk, elements_layout
from logger import g_logger, LogOutput, LogLevel
from apk_parser import ApkParser
from plugins import Plugin, PluginsManager
from enum import IntEnum
from tkinter import filedialog, Canvas
from pathlib import Path
from threading import Thread

# global vars holding tk, window, style and canvas instances
g_root = tk.Tk()
g_style = ttk.Style(g_root)

g_root.tk.call(
    "source", str(Path.cwd()) + 
    "\\themes\\breeze-dark\\breeze-dark.tcl"
)

g_win_w = 900
g_win_h = 500

# use breeze-dark theme
g_style.theme_use('breeze-dark')

# remove wanky dashed line which appears when tab is selected
g_style.configure("Tab", focuscolor=g_style.configure(".")["background"])

g_app = Window(g_root, g_win_w, g_win_h, "A-RE: Android")
g_canvas = Canvas(g_root, width=g_win_w, height=g_win_h)

g_apk_parser = None
g_current_file = None

# core elements ids that we will need throughout g_app lifecycle
class ECoreElements(IntEnum):
    NONE = 0,
    LOGGER = 1,
    APK_INFO_LABEL = 2,
    APK_ICON_VIEW = 3,
    PROGRESS_BAR = 4,
    TAB_CONTROL_ROOT = 5,
    TAB_CONTROL_PLUGINS = 6,
    GENERAL_TAB = 7,
    PLUGINS_TAB = 8,

def redirect_stdout(stdout) -> None:
    g_logger.external(stdout)

def decompile_apk_callback(threaded=False) -> None:
    if threaded == False: # hack, i'm too lazy to asyncify tkinter
        thread = Thread(target=decompile_apk_callback, args=(True,))
        thread.start()
        return

    global g_current_file, g_apk_parser

    file_path = filedialog.askopenfilename()

    if file_path == '': return

    _, file_name = os.path.split(file_path)
    g_current_file = file_path

    info_label = g_app.get_element_by_opt_id(ECoreElements.APK_INFO_LABEL)
    icon_view = g_app.get_element_by_opt_id(ECoreElements.APK_ICON_VIEW)
    progressbar = g_app.get_element_by_opt_id(ECoreElements.PROGRESS_BAR)

    progressbar.start()

    g_apk_parser = ApkParser(g_current_file, info_label, icon_view)

    if g_apk_parser.parse() != True:
        progressbar.stop()
        g_logger.error(f"[-] Failed to decompile: {g_current_file}\n")
        return

    g_root.title(f'A-RE: Android ({g_current_file})')

    decompile_cmd = f'java -Xmx1024m -jar {str(Path.cwd())}\\vendor\\apktool\\apktool.jar' \
        f" d {g_current_file} -o {str(Path.cwd())}\\decompiled\\{file_name}_decompiled -f"

    # decompiling file
    with subprocess.Popen(
        decompile_cmd, shell=True, stdout=subprocess.PIPE, 
        bufsize=1, universal_newlines=True
    ) as p:
        out, err = p.communicate()
        redirect_stdout(out)

    progressbar.stop()

    # logging
    g_logger.info(f"[+] Decompiled apk: {g_current_file}\n")

    
def recompile_apk_callback(threaded=False) -> None:
    if threaded == False: # hack, i'm too lazy to asyncify tkinter
        thread = Thread(target=decompile_apk_callback, args=(True,))
        thread.start()
        return

    global g_current_file, g_apk_parser

    _, file_name = os.path.split(g_current_file)

    # apktool b bar -o new_bar.apk
    recompile_cmd = f'java -Xmx1024m -jar {str(Path.cwd())}\\vendor\\apktool\\apktool.jar' \
        f" b {str(Path.cwd())}\\decompiled\\{file_name}_decompiled -o {str(Path.cwd())}\\build\\{file_name}_recompiled.apk"

    progressbar = g_app.get_element_by_opt_id(ECoreElements.PROGRESS_BAR)
    progressbar.start()

    # re-packing apk
    with subprocess.Popen(
        recompile_cmd, shell=True, stdout=subprocess.PIPE, 
        bufsize=1, universal_newlines=True
    ) as p:
        out, err = p.communicate()
        redirect_stdout(out)

    sign_cmd = f'java -jar {str(Path.cwd())}\\vendor\\apksigner\\apksigner.jar' \
        f' sign --key {str(Path.cwd())}\\vendor\\apksigner\\testkey.pk8' \
        f' --cert {str(Path.cwd())}\\vendor\\apksigner\\testkey.x509.pem' \
        f' {str(Path.cwd())}\\build\\{file_name}_recompiled.apk'

    # signing packed apk
    with subprocess.Popen(
        sign_cmd, shell=True, stdout=subprocess.PIPE, 
        bufsize=1, universal_newlines=True
    ) as p:
        out, err = p.communicate()
        redirect_stdout(out)

    # check if signed successfully
    g_apk_parser.set_apk(f'{str(Path.cwd())}\\build\\{file_name}_recompiled.apk')

    if g_apk_parser.is_signed():
        g_logger.info(f"[+] Signed apk: {g_current_file}_recompiled\n")
    else:
        g_logger.error(f'[!] Failed to sign apk: {g_current_file}_recompiled\n')
        progressbar.stop()
        return

    progressbar.stop()

    # logging
    g_logger.info(f"[+] Re-compiled apk: {g_current_file}_recompiled\n")


def construct_gui() -> None:
    global g_win_w, g_win_h

    tab_bar_root = g_app.create_tab_control(
        g_root, 20, 20, g_win_w, g_win_h, 
        ECoreElements.TAB_CONTROL_ROOT
    )

    general_tab = g_app.create_tab(tab_bar_root, 'General', ECoreElements.GENERAL_TAB)
    plugins_tab = g_app.create_tab(tab_bar_root, 'Plugins', ECoreElements.PLUGINS_TAB)

    tab_bar_plugins = g_app.create_tab_control(
        plugins_tab, 20, 20, g_win_w, g_win_h, 
        ECoreElements.TAB_CONTROL_PLUGINS
    )

    g_app.create_logbox(g_root, 600, 20, 280, 460, ECoreElements.LOGGER)
    logbox = g_app.get_element_by_opt_id(ECoreElements.LOGGER)

    logbox_level_colors = {
        LogLevel.INFO.tag:     { "foreground": "#FFFFFF", "background": None    },
        LogLevel.EXTERNAL.tag: { "foreground": "#39912D", "background": None    },
        LogLevel.SPECIAL.tag:  { "foreground": "#AAFF00", "background": None    },
        LogLevel.PLUGIN.tag:   { "foreground": "#00FFFF", "background": None    },
        LogLevel.WARNING.tag:  { "foreground": "yellow" , "background": None    },
        LogLevel.ERROR.tag:    { "foreground": "red"    , "background": "black" }
    }

    def setup_logbox(logger):
        for color in logbox_level_colors.items(): 
            logbox.tag_config(
                color[0], foreground=color[1]["foreground"],
                background=color[1]["background"]
            )
            
    g_logger.install_output(
        LogOutput(
            (lambda message, tag: logbox.insert('end', message, tag)), 
            setup_logbox
        )
    )

    g_logger.special(
        "A-RE android: android apps RE utility\n"
        "https://github.com/h4rdee/a-re-android\n\n"
    )

    plugins_manager = PluginsManager(g_app, tab_bar_plugins)

    g_app.create_button(
        general_tab, 20, 20, "Decompile APK", decompile_apk_callback,
        elements_layout["button"]["width"]
    )

    g_app.create_button(
        general_tab, 20 + elements_layout["button"]["width"] * 1, 20, "Re-build APK",  
        recompile_apk_callback, elements_layout["button"]["width"]
    )

    g_app.create_label(
        general_tab, 20, 20 + 50, 'APK info:'
    )

    g_app.create_label(
        general_tab, 20, 20 + 70, '< Load APK >',
        ECoreElements.APK_INFO_LABEL
    )

    g_app.create_image(
        general_tab, 20, 20 + 150, 0, 32, 32, 
        ECoreElements.APK_ICON_VIEW
    )

    g_app.create_progressbar(
        general_tab, -6, -7, 0, 0,
        ECoreElements.PROGRESS_BAR
    )

    g_canvas.pack()
    g_logger.info("[+] UI initialized\n")
    g_root.mainloop()


def main() -> None:
    construct_gui()
    return

if __name__ == '__main__':
    main()