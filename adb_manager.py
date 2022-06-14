from threading import Thread
import tkinter as tk

from logger import g_logger
from ppadb.client import Client as AdbClient
from ppadb.device import Device as AdbDevice

from utils import ECoreElements

class AdbManager:
    def __init__(self, gui) -> None:
        self.__client = None
        self.__is_connected = False
        self.__selected_device = None
        self.__ui_root = gui.get_adb_tab()
        self.__shell_command = tk.StringVar(self.__ui_root, '> ')
        self.__gui = gui
        self.__logger = g_logger
        self.__construct()

    def __construct(self) -> None:
        self.__settings_tab = self.__gui.create_tab(
            self.__gui.get_adb_tab_bar(), 520, 360, 'Settings'
        )

        self.__shell_tab = self.__gui.create_tab(
            self.__gui.get_adb_tab_bar(), 520, 360, 'Shell'
        )

        self.__gui.create_label(
            self.__settings_tab, 20, 20, 'IP:'
        )

        self.__adb_server_ip = tk.StringVar(self.__settings_tab)
        self.__adb_server_port = tk.StringVar(self.__settings_tab)

        self.__adb_server_ip.set('127.0.0.1')
        self.__adb_server_port.set('5037')

        self.__gui.create_editbox(
            self.__settings_tab, 20, 40, 
            self.__adb_server_ip, 100
        )

        self.__gui.create_label(
            self.__settings_tab, 130, 20, 'Port:'
        )

        self.__gui.create_editbox(
            self.__settings_tab, 130, 40, 
            self.__adb_server_port, 50
        )

        self.__gui.create_button(
            self.__settings_tab, 20, 80, 'Connect to ADB server',
            self.__adb_connect_callback, 160
        )

        self.__devices_label = self.__gui.create_label(
            self.__settings_tab, 20, 120, 
            'Devices list: (connect to adb server first)',
            ECoreElements.ADB_DEVICES_LABEL
        )

        self.__devices_cbx = self.__gui.create_combobox(
            self.__settings_tab, 20, 140, [],
            self.__selected_device_changed_callback,
            ECoreElements.ADB_DEVICES
        )

        self.__devices_cbx.focus_set()

        self.__shell_label = self.__gui.create_label(
            self.__shell_tab, 20, 20, 
            'Device shell (connect to adb server and select device first):',
            ECoreElements.ADB_SHELL_LABEL
        )

        self.__shell_terminal = self.__gui.create_terminal(
            self.__shell_tab, 20, 40, 480, 300, 
            self.__shell_command_callback,
            ECoreElements.ADB_SHELL_TERMINAL
        )

        # self.shell_terminal.insert('end', '> ')
        self.__shell_terminal.focus_set()

        self.__shell_terminal["state"] = "disabled"
        self.__devices_cbx["state"] = "disabled"

    def connect(self, host="127.0.0.1", port=5037):
        try:
            self.__client = AdbClient(host=host, port=port)
            self.__is_connected = True
            self.__logger.info(f'[+] [adb] Connected! Client version: {self.__client.version()}\n')
        except Exception as ex:
            self.__logger.error(f'[ !] [adb] {ex}\n')

    def is_connected(self) -> bool:
        return self.is_connected

    def get_adb_server_ip(self) -> str:
        return self.__adb_server_ip.get()

    def get_adb_server_port(self) -> str:
        return str(self.__adb_server_port.get())

    def get_devices_list(self) -> list:
        if self.__client == None:
            self.__logger.error(f'[ !] ADB client is not connected')
            return []

        result = []
        for device in self.__client.devices():
            result.append(device.serial)
    
        return result

    def get_device_by_serial(self, serial) -> AdbDevice:
        for device in self.__client.devices():
            if serial == device.serial:
                return device
        return None

    def set_selected_device(self, serial) -> None:
        self.__selected_device = serial

    def __shell_result_handler(self, connection) -> None:
        while True:
            data = connection.read(1024)
            if not data:
                break
            self.__shell_terminal.insert('end', f'> {data.decode("utf-8")}\n')
            self.__shell_terminal.yview_pickplace("end")

        connection.close()

    def __shell_command_callback(self, __none__=None, threaded=False) -> None:
        if threaded == False: # hack, i'm too lazy to asyncify tkinter
            thread = Thread(
                target=self.__shell_command_callback, 
                args=(self, True,)
            )
            thread.start()
            return

        terminal_content = self.__shell_terminal.get("1.0", "end-1c")
        self.__shell_command = terminal_content.split('\n')[-2].strip()

        self.__logger.info(f'[>] [adb] Executing "{self.__shell_command}" on {self.__selected_device}')

        device = self.__client.device(self.__selected_device)
        device.shell(self.__shell_command, handler=self.__shell_result_handler)
        
    def __adb_connect_callback(self, __none__=None, threaded=False) -> None:
        if threaded == False: # hack, i'm too lazy to asyncify tkinter
            thread = Thread(
                target=self.__adb_connect_callback, 
                args=(self, True,)
            )
            thread.start()
            return

        server_ip = self.__adb_server_ip.get()
        server_port = self.__adb_server_port.get()

        self.__logger.info(
            f'[>] [adb] Connecting to {server_ip}:{server_port}..\n'
        )

        self.connect(server_ip, int(server_port))
        devices = self.get_devices_list()

        if len(devices) == 0:
            self.__devices_label.config(text='< no devices >')
            self.set_selected_device(None)
            return

        self.__devices_label.config(text='Devices list:')

        self.__devices_cbx["state"] = "readonly"
        self.__shell_terminal["state"] = "normal"
        self.__devices_cbx["values"] = devices
        self.__devices_cbx.current(0)

        self.set_selected_device(self.__devices_cbx.get())

        self.__shell_label.config(text=f'Shell ({self.__devices_cbx.get()}):')

    def __selected_device_changed_callback(self, __none__=None, threaded=False) -> None:
        if threaded == False: # hack, i'm too lazy to asyncify tkinter
            thread = Thread(
                target=self.__selected_device_changed_callback, 
                args=(self, True,)
            )
            thread.start()
            return

        selected_device = self.__devices_cbx.get()
        self.set_selected_device(selected_device)

        self.__shell_label.config(text=f'Shell ({selected_device}):')
        self.__logger.info(f'[>] [adb] Changed device to {selected_device}\n')