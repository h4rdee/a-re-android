import os
import tkinter as tk

from logger import g_logger
from threading import Thread
from tkinter import filedialog

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
        self.__shell_cancelation_token = False
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

        self.__gui.get_adb_tab_bar().bind(
            '<<NotebookTabChanged>>', self.__on_tab_changed
        )

        self.__gui.create_label(
            self.__settings_tab, 20, 20, 'IP:'
        )

        self.__adb_server_ip = tk.StringVar(self.__settings_tab)
        self.__adb_server_port = tk.StringVar(self.__settings_tab)

        self.__adb_server_ip.set('127.0.0.1')
        self.__adb_server_port.set('5037')

        self.__ip_ebx = self.__gui.create_editbox(
            self.__settings_tab, 20, 40, 
            self.__adb_server_ip, 100
        )

        self.__port_ebx = self.__gui.create_label(
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

        self.__shell_label = self.__gui.create_label(
            self.__shell_tab, 20, 20, 
            'Device shell (connect to adb server and select device first):',
            ECoreElements.ADB_SHELL_LABEL
        )

        self.__shell_terminal = self.__gui.create_terminal(
            self.__shell_tab, 20, 40, 480, 270, 
            None, ECoreElements.ADB_SHELL_TERMINAL
        )

        self.__shell_executor = self.__gui.create_terminal(
            self.__shell_tab, 20, 310, 330, 30,
            self.__shell_command_callback,
            ECoreElements.ADB_SHELL_EXECUTOR
        )

        self.__save_terminal_btn = self.__gui.create_button(
            self.__shell_tab, 350, 310, 'save',
            self.__on_terminal_save, 60, 30
        )

        self.__kill_shell_thread_btn = self.__gui.create_button(
            self.__shell_tab, 410, 310, 'kill thread', 
            self.__invalidate_shell_cancelation_token, 90, 30
        )

        self.__shell_terminal["state"] = "disabled"
        self.__shell_executor["state"] = "disabled"
        self.__devices_cbx["state"] = "disabled"

    def connect(self, host="127.0.0.1", port=5037):
        try:
            self.__client = AdbClient(host=host, port=port)
            self.__is_connected = True
            self.__logger.info(f'[+] [adb] Connected! Client version: {self.__client.version()}\n')
        except Exception as ex:
            self.__logger.error(f'[ !] [adb] {ex}\n')

    def is_connected(self) -> bool:
        return self.__is_connected

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

    def __on_tab_changed(self, event):
        current_tab_index = event.widget.index("current")
        if current_tab_index == 0: # settings
            self.__ip_ebx.selection_clear() # tk selection bug?
            self.__settings_tab.focus_set()
        elif current_tab_index == 1: # shell
            self.__shell_executor.focus_set()

    def __refresh_shell_cancelation_token(self) -> None:
        self.__shell_cancelation_token = False

    def __invalidate_shell_cancelation_token(self) -> None:
        self.__logger.info('[>] [adb] Stopping shell thread..\n')
        self.__shell_cancelation_token = True

    def __terminal_print(self, data, recv=False) -> None:
        self.__shell_terminal["state"] = "normal"

        output = f'> {data}\n' if recv == False else f'{data}\n'
        self.__shell_terminal.insert('end', output)

        self.__shell_terminal["state"] = "disabled"
        self.__shell_terminal.yview_pickplace("end")
    
    def __on_terminal_save(self, __none__=None, threaded=False) -> None:
        if threaded == False: # hack, i'm too lazy to asyncify tkinter
            thread = Thread(
                target=self.__on_terminal_save, 
                args=(self, True,)
            )
            thread.start()
            return
        
        file_path = filedialog.asksaveasfile(
            mode='w', defaultextension=".txt",
        )

        if file_path == None: return
        
        file_cd, file_name = os.path.split(file_path.name)

        self.__logger.info(
            f'[>] [adb] Saving terminal output to {file_name}\n'
        )

        with open(file_path.name, "w") as terminal_output:
            terminal_content = str(
                self.__shell_terminal.get("1.0", tk.END)
            )

            terminal_output.write(terminal_content)
            terminal_output.close()

            self.__logger.info(
                f'[+] [adb] Saved terminal output to {file_name}\n'
            )

    def __on_device_lost(self) -> None:
        self.__logger.error('[ !] [adb] Lost device!\n')
        self.__devices_label.config(text='< no devices >')
        self.__devices_cbx.set('')
        self.__devices_cbx["values"] = []
        self.__devices_cbx["state"] = "disabled"
        self.__shell_label.config(text='Device shell (connect to adb server and select device first):')
        self.__terminal_print('lost device\n', True)
        self.__shell_executor["state"] = "disabled"
        self.set_selected_device(None)

    def __shell_result_handler(self, connection) -> None:
        while self.__shell_cancelation_token == False:
            data = connection.read(1024)
            if not data:
                break
            self.__terminal_print(data.decode("utf-8"), recv=True)

        connection.close()

    def __shell_command_callback(self, __none__=None, threaded=False) -> None:
        if threaded == False: # hack, i'm too lazy to asyncify tkinter
            thread = Thread(
                target=self.__shell_command_callback, 
                args=(self, True,)
            )
            thread.start()
            return

        self.__shell_command = self.__shell_executor.get("1.0", "end-1c").replace('\n', '')
        self.__logger.info(f'[>] [adb] Executing "{self.__shell_command}" on {self.__selected_device}\n')

        self.__refresh_shell_cancelation_token()
        self.__terminal_print(self.__shell_command)

        # clearing command buffer
        self.__shell_executor.delete('1.0', tk.END)

        device = self.__client.device(self.__selected_device)

        if device != None:
            device.shell(self.__shell_command, handler=self.__shell_result_handler)
        else:
            self.__on_device_lost()
        
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
        self.__shell_executor["state"] = "normal"
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