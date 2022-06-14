import os
import subprocess

from functools import partial
from pathlib import Path
from gui import elements_layout as el
from utils import ECoreElements
from threading import Thread
from tkinter import filedialog
from apk_parser import ApkParser

g_apk_parser = None
g_current_file = None

class ApkManager:
    def __init__(self, gui) -> None:
        self.gui = gui
        self.ui_root = gui.get_general_tab()
        self.construct()

    def construct(self) -> None:
        self.gui.create_button(
            self.ui_root, 20, 20, "Decompile APK", 
            self.decompile_apk_callback,
            el["button"]["width"]
        )

        self.gui.create_button(
            self.ui_root, 20 + el["button"]["width"] * 1, 20, "Re-build APK",  
            self.recompile_apk_callback, el["button"]["width"]
        )

        apk_info_label = self.gui.create_label(
            self.ui_root, 20, 20 + 50, 'APK info:'
        )

        apk_info_label.focus_set()

        self.gui.create_label(
            self.ui_root, 20, 20 + 70, '< Load APK >',
            ECoreElements.APK_INFO_LABEL
        )

        self.gui.create_image(
            self.ui_root, 20, 20 + 150, 0, 32, 32, 
            ECoreElements.APK_ICON_VIEW
        )

        self.gui.create_progressbar(
            self.ui_root, -6, -7, 0, 0,
            ECoreElements.PROGRESS_BAR
        )

    def decompile_apk_callback(self, __none__=None, threaded=False) -> None:
        if threaded == False: # hack, i'm too lazy to asyncify tkinter
            thread = Thread(
                target=self.decompile_apk_callback, 
                args=(self, True,)
            )
            thread.start()
            return

        global g_current_file, g_apk_parser

        file_path = filedialog.askopenfilename()

        if file_path == '': return

        _, file_name = os.path.split(file_path)
        g_current_file = file_path

        info_label = self.gui.get_element_by_opt_id(
            ECoreElements.APK_INFO_LABEL
        )

        icon_view = self.gui.get_element_by_opt_id(
            ECoreElements.APK_ICON_VIEW
        )

        progressbar = self.gui.get_element_by_opt_id(
            ECoreElements.PROGRESS_BAR
        )

        progressbar.start()

        g_apk_parser = ApkParser(g_current_file, info_label, icon_view)

        if g_apk_parser.parse() != True:
            progressbar.stop()
            self.gui.get_logger().error(f"[-] Failed to decompile: {g_current_file}\n")
            return

        self.gui.get_root().title(f'A-RE: Android ({g_current_file})')

        decompile_cmd = f'java -Xmx1024m -jar {str(Path.cwd())}\\vendor\\apktool\\apktool.jar' \
            f" d {g_current_file} -o {str(Path.cwd())}\\decompiled\\{file_name}_decompiled -f"

        # decompiling file
        with subprocess.Popen(
            decompile_cmd, shell=False, stdout=subprocess.PIPE, 
            bufsize=1, universal_newlines=True
        ) as p:
            out, err = p.communicate()
            self.gui.get_logger().external(out)

        progressbar.stop()

        # logging
        self.gui.get_logger().info(f"[+] Decompiled apk: {g_current_file}\n")

    #@staticmethod
    def recompile_apk_callback(self, __none__=None,threaded=False) -> None:
        if threaded == False: # hack, i'm too lazy to asyncify tkinter
            thread = Thread(
                target=self.recompile_apk_callback, 
                args=(self, True,)
            )
            thread.start()
            return

        global g_current_file, g_apk_parser

        if g_current_file == None:
            self.gui.get_logger().error(f'[ !] Nothing to re-compile\n')
            return

        _, file_name = os.path.split(g_current_file)

        recompile_cmd = f'java -Xmx1024m -jar {str(Path.cwd())}\\vendor\\apktool\\apktool.jar' \
            f" b {str(Path.cwd())}\\decompiled\\{file_name}_decompiled -o {str(Path.cwd())}\\build\\{file_name}_recompiled.apk"

        progressbar = self.gui.get_element_by_opt_id(
            ECoreElements.PROGRESS_BAR
        )

        progressbar.start()

        # re-packing apk
        with subprocess.Popen(
            recompile_cmd, shell=False, stdout=subprocess.PIPE, 
            bufsize=1, universal_newlines=True
        ) as p:
            out, err = p.communicate()
            self.gui.get_logger().external(out)

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
            self.gui.get_logger().external(out)

        # check if signed successfully
        g_apk_parser.set_apk(f'{str(Path.cwd())}\\build\\{file_name}_recompiled.apk')

        if g_apk_parser.is_signed():
            self.gui.get_logger().info(f"[+] Signed apk: {g_current_file}_recompiled\n")
        else:
            self.gui.get_logger().error(f'[ !] Failed to sign apk: {g_current_file}_recompiled\n')
            progressbar.stop()
            return

        progressbar.stop()

        # logging
        self.gui.get_logger().info(f"[+] Re-compiled apk: {g_current_file}_recompiled\n")