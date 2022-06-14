import callbacks

from functools import partial
from gui import elements_layout as el
from utils import ECoreElements

class ApkManager:
    def __init__(self, gui) -> None:
        self.gui = gui
        self.ui_root = gui.get_general_tab()
        self.construct()

    def construct(self) -> None:
        self.gui.create_button(
            self.ui_root, 20, 20, "Decompile APK", 
            partial(callbacks.decompile_apk_callback, self.gui),
            el["button"]["width"]
        )

        self.gui.create_button(
            self.ui_root, 20 + el["button"]["width"] * 1, 20, "Re-build APK",  
            partial(callbacks.recompile_apk_callback, self.gui), el["button"]["width"]
        )

        self.gui.create_label(
            self.ui_root, 20, 20 + 50, 'APK info:'
        )

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