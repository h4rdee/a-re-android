import os
import subprocess

from threading import Thread
from pathlib import Path
from tkinter import filedialog
from adb_manager import AdbManager
from apk_parser import ApkParser
from utils import ECoreElements

g_apk_parser = None
g_current_file = None

def decompile_apk_callback(gui, threaded=False) -> None:
    if threaded == False: # hack, i'm too lazy to asyncify tkinter
        thread = Thread(
            target=decompile_apk_callback, 
            args=(gui, True,)
        )
        thread.start()
        return

    global g_current_file, g_apk_parser

    file_path = filedialog.askopenfilename()

    if file_path == '': return

    _, file_name = os.path.split(file_path)
    g_current_file = file_path

    info_label = gui.get_element_by_opt_id(
        ECoreElements.APK_INFO_LABEL
    )

    icon_view = gui.get_element_by_opt_id(
        ECoreElements.APK_ICON_VIEW
    )

    progressbar = gui.get_element_by_opt_id(
        ECoreElements.PROGRESS_BAR
    )

    progressbar.start()

    g_apk_parser = ApkParser(g_current_file, info_label, icon_view)

    if g_apk_parser.parse() != True:
        progressbar.stop()
        gui.get_logger().error(f"[-] Failed to decompile: {g_current_file}\n")
        return

    gui.get_root().title(f'A-RE: Android ({g_current_file})')

    decompile_cmd = f'java -Xmx1024m -jar {str(Path.cwd())}\\vendor\\apktool\\apktool.jar' \
        f" d {g_current_file} -o {str(Path.cwd())}\\decompiled\\{file_name}_decompiled -f"

    # decompiling file
    with subprocess.Popen(
        decompile_cmd, shell=False, stdout=subprocess.PIPE, 
        bufsize=1, universal_newlines=True
    ) as p:
        out, err = p.communicate()
        gui.get_logger().external(out)

    progressbar.stop()

    # logging
    gui.get_logger().info(f"[+] Decompiled apk: {g_current_file}\n")

    
def recompile_apk_callback(gui, threaded=False) -> None:
    if threaded == False: # hack, i'm too lazy to asyncify tkinter
        thread = Thread(
            target=recompile_apk_callback, 
            args=(gui, True,)
        )
        thread.start()
        return

    global g_current_file, g_apk_parser

    if g_current_file == None:
        gui.get_logger().error(f'[ !] Nothing to re-compile\n')
        return

    _, file_name = os.path.split(g_current_file)

    recompile_cmd = f'java -Xmx1024m -jar {str(Path.cwd())}\\vendor\\apktool\\apktool.jar' \
        f" b {str(Path.cwd())}\\decompiled\\{file_name}_decompiled -o {str(Path.cwd())}\\build\\{file_name}_recompiled.apk"

    progressbar = gui.get_element_by_opt_id(
        ECoreElements.PROGRESS_BAR
    )

    progressbar.start()

    # re-packing apk
    with subprocess.Popen(
        recompile_cmd, shell=False, stdout=subprocess.PIPE, 
        bufsize=1, universal_newlines=True
    ) as p:
        out, err = p.communicate()
        gui.get_logger().external(out)

    sign_cmd = f'java -jar {str(Path.cwd())}\\vendor\\apksigner\\apksigner.jar' \
        f' sign --key {str(Path.cwd())}\\vendor\\apksigner\\testkey.pk8' \
        f' --cert {str(Path.cwd())}\\vendor\\apksigner\\testkey.x509.pem' \
        f' {str(Path.cwd())}\\build\\{file_name}_recompiled.apk'

    # signing packed apk
    with subprocess.Popen(
        sign_cmd, shell=False, stdout=subprocess.PIPE, 
        bufsize=1, universal_newlines=True
    ) as p:
        out, err = p.communicate()
        gui.get_logger().external(out)

    # check if signed successfully
    g_apk_parser.set_apk(f'{str(Path.cwd())}\\build\\{file_name}_recompiled.apk')

    if g_apk_parser.is_signed():
        gui.get_logger().info(f"[+] Signed apk: {g_current_file}_recompiled\n")
    else:
        gui.get_logger().error(f'[ !] Failed to sign apk: {g_current_file}_recompiled\n')
        progressbar.stop()
        return

    progressbar.stop()

    # logging
    gui.get_logger().info(f"[+] Re-compiled apk: {g_current_file}_recompiled\n")

def adb_connect_callback(adb_manager: AdbManager, threaded=False) -> None:
    if threaded == False: # hack, i'm too lazy to asyncify tkinter
        thread = Thread(
            target=adb_connect_callback, 
            args=(adb_manager, True,)
        )
        thread.start()
        return

    gui = adb_manager.get_gui()
    logger = gui.get_logger()

    server_ip = adb_manager.get_adb_server_ip()
    server_port = adb_manager.get_adb_server_port()

    logger.info(
        f'[>] [adb] Connecting to {server_ip}:{server_port}..\n'
    )

    adb_manager.connect(server_ip, int(server_port))

    devices_label = gui.get_element_by_opt_id(
        ECoreElements.ADB_DEVICES_LABEL
    )

    devices_cbx = gui.get_element_by_opt_id(
        ECoreElements.ADB_DEVICES
    )

    devices_label.config(text='Devices list:')
    devices_cbx["state"] = "readonly"
    devices_cbx["values"] = adb_manager.get_devices_list()
    devices_cbx.current(0)

def selected_device_changed_callback(adb_manager: AdbManager, threaded=False) -> None:
    if threaded == False: # hack, i'm too lazy to asyncify tkinter
        thread = Thread(
            target=selected_device_changed_callback, 
            args=(adb_manager, True,)
        )
        thread.start()
        return
    