import tkinter as tk
import callbacks

from logger import g_logger
from functools import partial
from ppadb.client import Client as AdbClient

from utils import ECoreElements

class AdbManager:
    def __init__(self, gui) -> None:
        self.client = None
        self.gui = gui
        self.ui_root = gui.get_adb_tab()
        self.logger = g_logger
        self.is_connected = False
        self.construct()

    def get_gui(self):
        return self.gui

    def construct(self) -> None:
        self.gui.create_label(
            self.ui_root, 20, 20, 'IP:'
        )

        self.adb_server_ip = tk.StringVar(self.ui_root)
        self.adb_server_port = tk.StringVar(self.ui_root)

        self.adb_server_ip.set('127.0.0.1')
        self.adb_server_port.set('5037')

        self.gui.create_editbox(
            self.ui_root, 20, 40, 
            self.adb_server_ip, 100
        )

        self.gui.create_label(
            self.ui_root, 130, 20, 'Port:'
        )

        self.gui.create_editbox(
            self.ui_root, 130, 40, 
            self.adb_server_port, 50
        )

        self.gui.create_button(
            self.ui_root, 20, 80, 'Connect to ADB server',
            partial(callbacks.adb_connect_callback, self), 160
        )

        self.devices_label = self.gui.create_label(
            self.ui_root, 20, 120, 
            'Devices list: (connect to adb server first)',
            ECoreElements.ADB_DEVICES_LABEL
        )

        self.devices_cbx = self.gui.create_combobox(
            self.ui_root, 20, 140, [],
            callbacks.selected_device_changed_callback,
            ECoreElements.ADB_DEVICES
        )

        self.devices_cbx["state"] = "disabled"

    def connect(self, host="127.0.0.1", port=5037):
        try:
            self.client = AdbClient(host=host, port=port)
            self.is_connected = True
            self.logger.info(f'[+] [adb] Connected! Client version: {self.client.version()}\n')
        except Exception as ex:
            self.logger.error(f'[ !] [adb] {ex}\n')

    def is_connected(self) -> bool:
        return self.is_connected

    def get_adb_server_ip(self) -> str:
        return self.adb_server_ip.get()

    def get_adb_server_port(self) -> str:
        return str(self.adb_server_port.get())

    def get_devices_list(self) -> list:
        if self.client == None:
            self.logger.error(f'[ !] ADB client is not connected')
            return []

        result = []
        for device in self.client.devices():
            result.append(device.serial)
    
        return result