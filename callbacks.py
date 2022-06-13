import os
import subprocess
import utils

from threading import Thread
from pathlib import Path
from tkinter import filedialog
from apk_parser import ApkParser
from utils import ECoreElements

g_apk_parser = None
g_current_file = None

def decompile_apk_callback(app, threaded=False) -> None:
    if threaded == False: # hack, i'm too lazy to asyncify tkinter
        thread = Thread(
            target=decompile_apk_callback, 
            args=(app, True,)
        )
        thread.start()
        return

    global g_current_file, g_apk_parser

    file_path = filedialog.askopenfilename()

    if file_path == '': return

    _, file_name = os.path.split(file_path)
    g_current_file = file_path

    info_label = app.get_element_by_opt_id(
        ECoreElements.APK_INFO_LABEL
    )

    icon_view = app.get_element_by_opt_id(
        ECoreElements.APK_ICON_VIEW
    )

    progressbar = app.get_element_by_opt_id(
        ECoreElements.PROGRESS_BAR
    )

    progressbar.start()

    g_apk_parser = ApkParser(g_current_file, info_label, icon_view)

    if g_apk_parser.parse() != True:
        progressbar.stop()
        app.get_logger().error(f"[-] Failed to decompile: {g_current_file}\n")
        return

    app.get_root().title(f'A-RE: Android ({g_current_file})')

    decompile_cmd = f'java -Xmx1024m -jar {str(Path.cwd())}\\vendor\\apktool\\apktool.jar' \
        f" d {g_current_file} -o {str(Path.cwd())}\\decompiled\\{file_name}_decompiled -f"

    # decompiling file
    with subprocess.Popen(
        decompile_cmd, shell=True, stdout=subprocess.PIPE, 
        bufsize=1, universal_newlines=True
    ) as p:
        out, err = p.communicate()
        app.get_logger().external(out)

    progressbar.stop()

    # logging
    app.get_logger().info(f"[+] Decompiled apk: {g_current_file}\n")

    
def recompile_apk_callback(app, threaded=False) -> None:
    if threaded == False: # hack, i'm too lazy to asyncify tkinter
        thread = Thread(
            target=recompile_apk_callback, 
            args=(app, True,)
        )
        thread.start()
        return

    global g_current_file, g_apk_parser

    _, file_name = os.path.split(g_current_file)

    recompile_cmd = f'java -Xmx1024m -jar {str(Path.cwd())}\\vendor\\apktool\\apktool.jar' \
        f" b {str(Path.cwd())}\\decompiled\\{file_name}_decompiled -o {str(Path.cwd())}\\build\\{file_name}_recompiled.apk"

    progressbar = app.get_element_by_opt_id(
        ECoreElements.PROGRESS_BAR
    )

    progressbar.start()

    # re-packing apk
    with subprocess.Popen(
        recompile_cmd, shell=True, stdout=subprocess.PIPE, 
        bufsize=1, universal_newlines=True
    ) as p:
        out, err = p.communicate()
        app.get_logger().external(out)

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
        utils.redirect_stdout(app.get_logger(), out)

    # check if signed successfully
    g_apk_parser.set_apk(f'{str(Path.cwd())}\\build\\{file_name}_recompiled.apk')

    if g_apk_parser.is_signed():
        app.get_logger().info(f"[+] Signed apk: {g_current_file}_recompiled\n")
    else:
        app.get_logger().error(f'[ !] Failed to sign apk: {g_current_file}_recompiled\n')
        progressbar.stop()
        return

    progressbar.stop()

    # logging
    app.get_logger().info(f"[+] Re-compiled apk: {g_current_file}_recompiled\n")