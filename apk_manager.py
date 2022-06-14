import os
import subprocess

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
        self.__gui = gui
        self.__logger = gui.get_logger()
        self.__app_root = gui.get_root()
        self.__ui_root = gui.get_general_tab()
        self.__construct()

    def __construct(self) -> None:
        self.__gui.create_button(
            self.__ui_root, 20, 20, "Decompile APK", 
            self.__decompile_apk_callback,
            el["button"]["width"]
        )

        self.__gui.create_button(
            self.__ui_root, 20 + el["button"]["width"] * 1, 20, "Re-build APK",  
            self.__recompile_apk_callback, el["button"]["width"]
        )

        self.__apk_info_label = self.__gui.create_label(
            self.__ui_root, 20, 20 + 50, 'APK info:'
        )

        self.__apk_info_label.focus_set()

        self.__apk_sub_info_label = self.__gui.create_label(
            self.__ui_root, 20, 20 + 70, '< Load APK >',
            ECoreElements.APK_INFO_LABEL
        )

        self.__apk_icon_view = self.__gui.create_image(
            self.__ui_root, 20, 20 + 150, 0, 32, 32, 
            ECoreElements.APK_ICON_VIEW
        )

        self.__progressbar = self.__gui.create_progressbar(
            self.__ui_root, -6, -7, 0, 0,
            ECoreElements.PROGRESS_BAR
        )

    def __decompile_apk_callback(self, __none__=None, threaded=False) -> None:
        if threaded == False: # hack, i'm too lazy to asyncify tkinter
            thread = Thread(
                target=self.__decompile_apk_callback, 
                args=(self, True,)
            )
            thread.start()
            return

        global g_current_file, g_apk_parser

        file_path = filedialog.askopenfilename()

        if file_path == '': return

        _, file_name = os.path.split(file_path)
        g_current_file = file_path

        self.__progressbar.start()

        g_apk_parser = ApkParser(
            g_current_file, self.__apk_sub_info_label, 
            self.__apk_icon_view
        )

        if g_apk_parser.parse() != True:
            self.__progressbar.stop()
            self.__logger.error(f"[-] Failed to decompile: {g_current_file}\n")
            return

        self.__app_root.title(f'A-RE: Android ({g_current_file})')

        decompile_cmd = f'java -Xmx1024m -jar {str(Path.cwd())}\\vendor\\apktool\\apktool.jar' \
            f" d {g_current_file} -o {str(Path.cwd())}\\decompiled\\{file_name}_decompiled -f"

        # decompiling file
        with subprocess.Popen(
            decompile_cmd, shell=False, stdout=subprocess.PIPE, 
            bufsize=1, universal_newlines=True
        ) as p:
            out, err = p.communicate()
            self.__logger.external(out)

        self.__progressbar

        # logging
        self.__logger.info(f"[+] Decompiled apk: {g_current_file}\n")

    #@staticmethod
    def __recompile_apk_callback(self, __none__=None,threaded=False) -> None:
        if threaded == False: # hack, i'm too lazy to asyncify tkinter
            thread = Thread(
                target=self.__recompile_apk_callback, 
                args=(self, True,)
            )
            thread.start()
            return

        global g_current_file, g_apk_parser

        if g_current_file == None:
            self.__logger.error(f'[ !] Nothing to re-compile\n')
            return

        _, file_name = os.path.split(g_current_file)

        recompile_cmd = f'java -Xmx1024m -jar {str(Path.cwd())}\\vendor\\apktool\\apktool.jar' \
            f" b {str(Path.cwd())}\\decompiled\\{file_name}_decompiled -o {str(Path.cwd())}\\build\\{file_name}_recompiled.apk"

        self.__progressbar.start()

        # re-packing apk
        with subprocess.Popen(
            recompile_cmd, shell=False, stdout=subprocess.PIPE, 
            bufsize=1, universal_newlines=True
        ) as p:
            out, err = p.communicate()
            self.__logger.external(out)

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
            self.__logger.external(out)

        # check if signed successfully
        g_apk_parser.set_apk(f'{str(Path.cwd())}\\build\\{file_name}_recompiled.apk')

        if g_apk_parser.is_signed():
            self.__logger.info(f"[+] Signed apk: {g_current_file}_recompiled\n")
        else:
            self.__logger.error(f'[ !] Failed to sign apk: {g_current_file}_recompiled\n')
            self.__progressbar.stop()
            return

        self.__progressbar.stop()

        # logging
        self.__logger.info(f"[+] Re-compiled apk: {g_current_file}_recompiled\n")