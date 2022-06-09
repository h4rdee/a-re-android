from pyaxmlparser import APK
import tkinter as tk
from logger import Logger, g_logger, LogOutput, LogLevel

# apk parser wrapper
class ApkParser:
    def __init__(self, apk_path: str, info_label, icon_view) -> None:
        self.set_apk(apk_path)
        self.info_label = info_label
        self.icon_view = icon_view

    # update apk info (might be useful to check apk info afrer making changes to it)
    def set_apk(self, apk_path: str) -> None:
        self.apk_path = apk_path
        self.apk = APK(apk_path)
    
    # apk parsing routine
    def parse(self) -> None:
        info_string = f'package: {self.apk.package}\n' \
            f'version: {self.apk.version_name}\n' \
            f'version code: {self.apk.version_code}\n' \
            f'application: {self.apk.application}'

        # updating corresponding label..
        self.info_label.config(text=info_string)

        #..and icon
        icon = tk.PhotoImage(data=self.apk.icon_data, format='png')
        self.icon_view.configure(image=icon)
        self.icon_view.image=icon

        g_logger.info('[+] Parsed apk info\n')

    # checks whether apk is signed or not
    def is_signed(self, apk_path='') -> bool:
        if not apk_path:
            apk_path = self.apk_path
        apk = APK(apk_path)
        return apk.is_signed()