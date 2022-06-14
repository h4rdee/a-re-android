from threading import Thread
import tkinter as tk

from logger import g_logger
from functools import partial
from ppadb.client import Client as AdbClient
from ppadb.device import Device as AdbDevice

from utils import ECoreElements

class AdbManager:
    def __init__(self, gui) -> None:
        self.client = None
        self.selected_device = None
        self.gui = gui
        self.ui_root = gui.get_adb_tab()
        self.logger = g_logger
        self.shell_command = tk.StringVar(self.ui_root, '> ')
        self.is_connected = False
        self.construct()
        
    def get_gui(self):
        return self.gui

    def construct(self) -> None:
        self.settings_tab = self.gui.create_tab(
            self.gui.get_adb_tab_bar(), 520, 360, 'Settings'
        )

        self.shell_tab = self.gui.create_tab(
            self.gui.get_adb_tab_bar(), 520, 360, 'Shell'
        )

        self.gui.create_label(
            self.settings_tab, 20, 20, 'IP:'
        )

        self.adb_server_ip = tk.StringVar(self.settings_tab)
        self.adb_server_port = tk.StringVar(self.settings_tab)

        self.adb_server_ip.set('127.0.0.1')
        self.adb_server_port.set('5037')

        self.gui.create_editbox(
            self.settings_tab, 20, 40, 
            self.adb_server_ip, 100
        )

        self.gui.create_label(
            self.settings_tab, 130, 20, 'Port:'
        )

        self.gui.create_editbox(
            self.settings_tab, 130, 40, 
            self.adb_server_port, 50
        )

        self.gui.create_button(
            self.settings_tab, 20, 80, 'Connect to ADB server',
            partial(self.adb_connect_callback, self), 160
        )

        self.devices_label = self.gui.create_label(
            self.settings_tab, 20, 120, 
            'Devices list: (connect to adb server first)',
            ECoreElements.ADB_DEVICES_LABEL
        )

        self.devices_cbx = self.gui.create_combobox(
            self.settings_tab, 20, 140, [],
            partial(self.selected_device_changed_callback, self),
            ECoreElements.ADB_DEVICES
        )

        self.devices_cbx.focus_set()

        self.shell_label = self.gui.create_label(
            self.shell_tab, 20, 20, 
            'Device shell (connect to adb server and select device first):',
            ECoreElements.ADB_SHELL_LABEL
        )

        self.shell_terminal = self.gui.create_terminal(
            self.shell_tab, 20, 40, 480, 300, 
            self.shell_command_callback,
            ECoreElements.ADB_SHELL_TERMINAL
        )

        # self.shell_terminal.insert('end', '> ')
        self.shell_terminal.focus_set()

        self.shell_terminal["state"] = "disabled"
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

    def get_device_by_serial(self, serial) -> AdbDevice:
        for device in self.client.devices():
            if serial == device.serial:
                return device
        return None

    def set_selected_device(self, serial) -> None:
        self.selected_device = serial

    def shell_result_handler(self, connection) -> None:
        while True:
            data = connection.read(1024)
            if not data:
                break
            self.shell_terminal.insert('end', f'> {data.decode("utf-8")}\n')
            self.shell_terminal.yview_pickplace("end")

        connection.close()

    def shell_command_callback(self, __none__=None, threaded=False) -> None:
        if threaded == False: # hack, i'm too lazy to asyncify tkinter
            thread = Thread(
                target=self.shell_command_callback, 
                args=(self, True,)
            )
            thread.start()
            return

        terminal_content = self.shell_terminal.get("1.0", "end-1c")
        self.shell_command = terminal_content.split('\n')[-2].strip()

        self.logger.info(f'[>] [adb] Executing "{self.shell_command}" on {self.selected_device}')

        device = self.client.device(self.selected_device)
        device.shell(self.shell_command, handler=self.shell_result_handler)
        
    def adb_connect_callback(self, __none__=None, threaded=False) -> None:
        if threaded == False: # hack, i'm too lazy to asyncify tkinter
            thread = Thread(
                target=self.adb_connect_callback, 
                args=(self, True,)
            )
            thread.start()
            return

        gui = self.get_gui()
        logger = gui.get_logger()

        server_ip = self.get_adb_server_ip()
        server_port = self.get_adb_server_port()

        logger.info(
            f'[>] [adb] Connecting to {server_ip}:{server_port}..\n'
        )

        self.connect(server_ip, int(server_port))
        devices = self.get_devices_list()

        if len(devices) == 0:
            self.devices_label.config(text='< no devices >')
            self.set_selected_device(None)
            return

        self.devices_label.config(text='Devices list:')

        self.devices_cbx["state"] = "readonly"
        self.shell_terminal["state"] = "normal"
        self.devices_cbx["values"] = devices
        self.devices_cbx.current(0)

        self.set_selected_device(self.devices_cbx.get())

        self.shell_label.config(text=f'Shell ({self.devices_cbx.get()}):')

    def selected_device_changed_callback(self, __none__=None, threaded=False) -> None:
        if threaded == False: # hack, i'm too lazy to asyncify tkinter
            thread = Thread(
                target=self.selected_device_changed_callback, 
                args=(self, True,)
            )
            thread.start()
            return

        gui = self.get_gui()
        logger = gui.get_logger()

        selected_device = self.devices_cbx.get()
        self.set_selected_device(selected_device)

        self.shell_label.config(text=f'Shell ({selected_device}):')

        logger.info(f'[>] [adb] Changed device to {selected_device}\n')