import tkinter as tk

# Cocos2D jsc/jsc2/luac plugin for unpacking & repacking plugin for A:RE android
class Cocos2D:
    def __init__(self, gui, ui_root, logger) -> None:
        self.gui = gui
        self.ui_root = ui_root
        self.logger = logger
        self.load()

    def click(self):
        self.logger.info('click\n')
    
    def load(self) -> None:
        self.logger.info('[!] hello from Cocos2D plugin\n')
        self.gui.create_button(
            self.ui_root, 20, 110, "Test", self.click
        )

def __init__(gui, ui_root, logger) -> None:
    plugin = Cocos2D(gui, ui_root, logger)