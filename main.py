# todo:
# - layout scheme for elements

from gui import Window, tk, ttk
from plugins import PluginsManager
from tkinter import Canvas
from pathlib import Path

# global vars holding tk, window, style and canvas instances
g_root = tk.Tk()
g_style = ttk.Style(g_root)

g_root.tk.call(
    "source", str(Path.cwd()) + 
    "\\themes\\breeze-dark\\breeze-dark.tcl"
)

g_win_w = 900
g_win_h = 500

# use breeze-dark theme
g_style.theme_use('breeze-dark')

# remove wanky dashed line which appears when tab is selected
g_style.configure("Tab", focuscolor=g_style.configure(".")["background"])

g_app = Window(g_root, g_win_w, g_win_h, "A-RE: Android")
g_canvas = Canvas(g_root, width=g_win_w, height=g_win_h)

def init() -> None:
    g_app.construct()
    
    g_logger = g_app.get_logger()
    g_logger.special(
        "A-RE android: android apps RE utility\n"
        "https://github.com/h4rdee/a-re-android\n\n"
    )

    plugins_manager = PluginsManager(g_app)

    g_canvas.pack()
    g_logger.info("[+] UI initialized\n")
    g_root.mainloop()


def main() -> None:
    init()

if __name__ == '__main__':
    main()