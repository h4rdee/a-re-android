import os
import tkinter as tk
import zlib
import xxtea
import webbrowser

from threading import Thread
from tkinter import filedialog, messagebox

# Cocos2D jsc/jsc2/luac plugin for unpacking & repacking plugin for A:RE android
class Cocos2D:
    def __init__(self, plugin_obj, gui) -> None:
        self.__plugin_obj = plugin_obj
        self.__gui = gui
        self.__ui_root = gui.get_plugins_tab_bar()
        self.__logger = gui.get_logger()
        self.__xxtea_key = tk.StringVar(self.__ui_root)
        self.__valid_dec_extensions = ['jsc', 'jsc2', 'luac']
        self.__valid_enc_extensions = ['js', 'lua']
        self.__load()

    def __decrypt(self, threaded=False) -> None:
        if threaded == False: # hack, i'm too lazy to asyncify tkinter
            thread = Thread(target=self.__decrypt, args=(True,))
            thread.start()
            return

        if len(self.__xxtea_key.get()) != 16:
            self.__logger.plugin(
                f'[ !] [{self.__plugin_obj.get_plugin_name()}]' \
                ' Key should be 16-bytes long!\n'
            )
            return

        file_path = filedialog.askopenfilename()
        if file_path == '': return

        file_cd, file_name = os.path.split(file_path)
        file_ext = file_name.split('.')[-1]
        
        is_valid_extension = False

        for ext in self.__valid_dec_extensions:
            if ext == file_ext:
                is_valid_extension = True
                break

        if is_valid_extension == False:
            self.__logger.plugin(
                f'[ !] [{self.__plugin_obj.get_plugin_name()}]' \
                ' Invalid file extension\n'
            )
            return

        self.__logger.plugin(
            f'[>] [{self.__plugin_obj.get_plugin_name()}] Decrypting {file_name} using key:' \
            f' {self.__xxtea_key.get()}\n'
        )
        
        with open(file_path, "rb") as encrypted_file:
            encrypted_raw = encrypted_file.read()
            try:
                decrypted_data = xxtea.decrypt(encrypted_raw, self.__xxtea_key.get())
                if len(decrypted_data) == 0:
                    self.__logger.plugin(
                        f"[ -] [{self.__plugin_obj.get_plugin_name()}]" \
                        f" Decrypted data len == 0, provided key is probably wrong\n"
                    )
                    return

                decrypted_file_ext = "lua" if file_ext == 'luac' else 'js'
                with open(os.path.join(file_cd, f"{file_name}.{decrypted_file_ext}"), "wb") as decrypted_file:
                    if decrypted_data[0:2] == b'\x1f\x8b': # is decrypted file packed? (gzip)

                        do_decompress = messagebox.askyesno(
                            f"{self.__plugin_obj.get_plugin_name()}", 
                            f"{file_name} was successfully decrypted," \
                            " and appears to be compressed (gzip)\n" \
                            "Do you want decompress it?"
                        )

                        if do_decompress == True:
                            try:
                                decompressed_data = zlib.decompress(decrypted_data, zlib.MAX_WBITS | 32)
                                self.__logger.plugin(
                                    f"[+] [{self.__plugin_obj.get_plugin_name()}]" \
                                    f" Successfully decompressed {file_name}\n"
                                )
                                decrypted_data = decompressed_data
                            except Exception as ex:
                                self.__logger.plugin(
                                    f"[-] [{self.__plugin_obj.get_plugin_name()}]" \
                                    f" Failed to decompress {file_name}\n"
                                )
                                return
   
                    decrypted_file.write(decrypted_data)
                    self.__logger.plugin(
                        f"[+] [{self.__plugin_obj.get_plugin_name()}]" \
                        f" {file_name} successfully decrypted\n"
                    )
            except Exception as ex:
                self.logger.__plugin(
                    f'[ !] [{self.__plugin_obj.get_plugin_name()}] {ex}\n'
                )
                return

    def __encrypt(self, threaded=False) -> None:
        if threaded == False: # hack, i'm too lazy to asyncify tkinter
            thread = Thread(target=self.__encrypt, args=(True,))
            thread.start()
            return

        if len(self.__xxtea_key.get()) != 16:
            self.__logger.plugin(
                f'[ !] [{self.__plugin_obj.get_plugin_name()}]' \
                ' Key should be 16-bytes long!\n'
            )
            return

        file_path = filedialog.askopenfilename()
        if file_path == '': return

        file_cd, file_name = os.path.split(file_path)
        file_ext = file_name.split('.')[-1]

        is_valid_extension = False

        for ext in self.__valid_enc_extensions:
            if ext == file_ext:
                is_valid_extension = True
                break

        if is_valid_extension == False:
            self.__logger.plugin(
                f'[ !] [{self.__plugin_obj.get_plugin_name()}]' \
                ' Invalid file extension\n'
            )
            return
        
        self.__logger.plugin(
            f'[>] [{self.__plugin_obj.get_plugin_name()}] Encrypting {file_name} using key:' \
            f' {self.__xxtea_key.get()}\n'
        )

        with open(file_path, "rb") as file:
            file_raw = file.read()
            try:
                encrypted_file_ext = "luac" if file_ext == 'lua' else 'jsc'
                with open(
                    os.path.join(
                        file_cd, 
                        f"{file_name.split('.')[0]}.{encrypted_file_ext}"
                    ), "wb"
                ) as encrypted_file:
                    do_compress = messagebox.askyesno(
                        f"{self.__plugin_obj.get_plugin_name()}", 
                        f"Do you want to compress {file_name} before encrypting? (gzip)"
                    )

                    if do_compress == True:
                        try:
                            compressed_data = zlib.compress(file_raw, 6)
                            self.__logger.plugin(
                                f"[+] [{self.__plugin_obj.get_plugin_name()}]" \
                                f" Successfully compressed {file_name}\n"
                            )
                            encrypted_data = xxtea.encrypt(compressed_data, self.__xxtea_key.get())
                        except Exception as ex:
                            self.__logger.plugin(
                                f"[-] [{self.__plugin_obj.get_plugin_name()}]" \
                                f" Failed to compress {file_name}\n"
                            )
                            return
                    else:
                        encrypted_data = xxtea.encrypt(file_raw, self.__xxtea_key.get())

                    encrypted_file.write(encrypted_data)

                    self.__logger.plugin(
                        f"[+] [{self.__plugin_obj.get_plugin_name()}]" \
                        f" {file_name} successfully encrypted\n"
                    )

            except Exception as ex:
                self.logger.plugin(
                    f'[ !] [{self.__plugin_obj.get_plugin_name()}] {ex}\n'
                )
                return
    
    def __load(self) -> None:
        self.__logger.plugin(
            f'[>] [{self.__plugin_obj.get_plugin_name()}] Initializing GUI\n'
        )

        self.__gui.create_link(
            self.__ui_root, 21, 90, 
            self.__plugin_obj.get_plugin_documentation_link(),
            lambda c: webbrowser.open_new_tab(
                self.__plugin_obj.get_plugin_documentation_link()
            )
        )

        self.__gui.create_label(self.__ui_root, 20, 120, "16-byte xxtea key:" )

        self.__gui.create_editbox(
            self.__ui_root, 20, 140,
            self.__xxtea_key, 173
        )

        self.__gui.create_button(
            self.__ui_root, 20, 180, 
            "Decrypt JSC/JSC2/LUAC", 
            self.__decrypt, 172, 30
        )

        self.__gui.create_button(
            self.__ui_root, 20, 210, 
            "Encrypt JS/LUA", 
            self.__encrypt, 172, 30
        )


def __init__(plugin_obj, gui) -> None:
    plugin = Cocos2D(plugin_obj, gui)