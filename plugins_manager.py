import json
import os

from importlib.machinery import SourceFileLoader
from pathlib import Path
from logger import g_logger

class Plugin:
    def __init__(self, path) -> None:
        json_cfg = None

        self.__plugin_path = path

        plugin_config = path + "\\config.json"
        plugin_config = Path(plugin_config)

        self.__is_valid = False

        if plugin_config.exists() == False:
            g_logger.warning('[!] Missing plugin config\n')
            return

        with open(plugin_config) as cfg:
            try:
                json_cfg = json.load(cfg)
                if not 'plugin_name' in json_cfg or not 'plugin_desc' in json_cfg or \
                    not 'plugin_author' in json_cfg or not 'plugin_doc' in json_cfg or \
                        not 'plugin_ver' in json_cfg or not 'plugin_entry' in json_cfg:
                            g_logger.warning('[!] Invalid plugin config\n')
                            return
            except Exception as ex:
                g_logger.error(f'[!] {ex}\n')
                return

        self.__json_cfg = json_cfg
        self.__is_valid = True

    def is_valid_plugin(self) -> bool:
        return self.__is_valid

    def get_plugin_name(self) -> str:
        return self.__json_cfg['plugin_name']

    def get_plugin_description(self) -> str:
        return self.__json_cfg['plugin_desc']

    def get_plugin_author(self) -> str:
        return self.__json_cfg['plugin_author']

    def get_plugin_documentation_link(self) -> str:
        return self.__json_cfg['plugin_doc']

    def get_plugin_major_version(self) -> int:
        return self.__json_cfg['plugin_ver']['major']
    
    def get_plugin_minor_version(self) -> int:
        return self.__json_cfg['plugin_ver']['minor']

    def get_plugin_version_string(self) -> str:
        return f"{self.__json_cfg['plugin_ver']['major']}.{self.__json_cfg['plugin_ver']['minor']}"

    def load(self, gui) -> None: # todo: return load-status from plugin
        try:
            plugin_module = self.__plugin_path + f"\\{self.__json_cfg['plugin_entry']}"
            plugin = SourceFileLoader(os.path.basename(self.__plugin_path), plugin_module).load_module()
            plugin.__init__(self, gui)
        except Exception as ex:
            g_logger.warning(f'[!] {ex}\n')
            g_logger.error(f'[-] Failed to load {self.get_plugin_name()} plugin\n')

class PluginsManager:
    __plugins_list = []
    __plugins_tabs = []

    def __init__(self, gui) -> None:
        self.__gui = gui
        self.__logger = gui.get_logger()

        self.__logger.info('[>] Scanning for plugins..\n')

        subfolders = [ f.path for f in os.scandir(str(Path.cwd()) + "\\plugins") if f.is_dir() ]

        for folder in subfolders:
            plugin_name = os.path.basename(folder)
            self.__logger.info(f'[>] Scanning {plugin_name}..\n')
            plugin = Plugin(folder)

            if plugin.is_valid_plugin() == True:
                self.__logger.info(f'[+] {plugin.get_plugin_name()} is valid plugin\n')

                self.__plugins_list.append(plugin)

                tab = self.__gui.create_tab(
                    self.__gui.get_plugins_tab_bar(), 
                    520, 360, plugin.get_plugin_name()
                )

                self.__plugins_tabs.append(tab)

                self.__gui.create_label(
                    self.__plugins_tabs[-1], 20, 20, 
                    f'{plugin.get_plugin_name()} v{plugin.get_plugin_version_string()} ' +
                    f'by {plugin.get_plugin_author()}\n{plugin.get_plugin_description()}\n' +
                    f'Documentation: \n'
                )

                plugin.load(self.__gui)
            else:
                self.__logger.info(f'[-] {plugin_name} isn\'t valid plugin\n')

    def get_plugins_list(self) -> list[Plugin]:
        return self.__plugins_list