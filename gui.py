import tkinter as tk
import tkinter.font as tkFont

from tkinter import ttk
from typing import Any
from logger import g_logger
from utils import ECoreElements

from functools import partial

elements_layout = {
    "button": {"width": 120, "height": 30}
}

class Window:
    log_font = None
    elements = { None: None }

    def __init__(self, root, w, h, title):
        root.title(title)
        width=w; height=h

        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()

        align_str = f"{width}x{height}+{int((screenwidth-width)/2)}+{int((screenheight-height)/2)}"

        root.geometry(align_str)
        root.resizable(width=False, height=False)

        self.logger = g_logger
        self.root = root
        self.w = width
        self.h = height
        self.log_font = tkFont.Font(family="Helvetica", size=10)
        self.terminal_font = tkFont.Font(family="Helvetica", size=9)

    def construct(self):
        self.tab_bar_root = self.create_tab_control(
            self.root, 20, 20, self.w, self.h, 
            ECoreElements.TAB_CONTROL_ROOT
        )

        self.general_tab = self.create_tab(
            self.tab_bar_root, self.w-340, self.h-70,
            'General', ECoreElements.GENERAL_TAB
        )

        self.adb_tab = self.create_tab(
            self.tab_bar_root, self.w-340, self.h-70,
            'ADB', ECoreElements.ADB_TAB
        )

        self.tab_bar_adb = self.create_tab_control(
            self.adb_tab, 20, 20, self.w, self.h,
            ECoreElements.TAB_CONTROL_ADB
        )

        self.plugins_tab = self.create_tab(
            self.tab_bar_root, self.w-340, self.h-70,
            'Plugins', ECoreElements.PLUGINS_TAB
        )

        self.tab_bar_plugins = self.create_tab_control(
            self.plugins_tab, 20, 20, self.w, self.h, 
            ECoreElements.TAB_CONTROL_PLUGINS
        )

        self.create_logbox(
            self.root, 600, 20, 280, 460, ECoreElements.LOGGER
        )

        self.logger.construct(self)

    def get_root(self):
        return self.root

    def get_logger(self):
        return self.logger

    def get_general_tab(self) -> ttk.Notebook:
        return self.general_tab

    def get_adb_tab(self) -> ttk.Notebook:
        return self.adb_tab
    
    def get_plugins_tab_bar(self) -> ttk.Notebook:
        return self.tab_bar_plugins

    def get_adb_tab_bar(self) -> ttk.Notebook:
        return self.tab_bar_adb

    def get_element_by_opt_id(self, opt_id) -> Any:
        el = self.elements.get(opt_id)
        if el is None:
            g_logger.error(f"[ !] element with opt_id {opt_id} not found\n")
        return el

    def push_external_element(self, element, id: int) -> None:
        if id != 0:
            self.elements[id] = element
        else:
            g_logger.warning(
                "[ !] skipping element: external elements must have an id\n"
            )

    def create_button(self, root, xpos: int, ypos: int, label: str, 
        callback, width=72, height=30, opt_id=0) -> ttk.Button:

        temp_btn = ttk.Button(root, text=label, command=callback)
        temp_btn.place(x=xpos, y=ypos, width=width, height=height)

        if opt_id != 0:
            self.elements[opt_id] = temp_btn

        return temp_btn

    def create_label(self, root, xpos: int, ypos: int, label: str, opt_id=0) -> ttk.Label:
        temp_lbl = ttk.Label(root, text=label)
        temp_lbl.place(x=xpos, y=ypos)

        if opt_id != 0:
            self.elements[opt_id] = temp_lbl

        return temp_lbl

    def create_editbox(self, root, xpos: int, ypos: int, var: tk.StringVar, 
        width=70, height=30, opt_id=0) -> ttk.Entry:

        temp_ebx = ttk.Entry(root, textvariable=var)
        # temp_ebx.insert(0, var.get())
        temp_ebx.place(x=xpos, y=ypos, width=width, height=height)

        if opt_id != 0:
            self.elements[opt_id] = temp_ebx

        return temp_ebx

    def create_slider(self, root, xpos: int, ypos: int,
        min: float, max: float, orient: str, callback, opt_id=0) -> ttk.Scale:

        temp_sld = ttk.Scale(
            root, command=callback, 
            from_=min, to=max, orient=orient, 
        )
        temp_sld.place(x=xpos, y=ypos, height=150)
        if opt_id != 0:
            self.elements[opt_id] = temp_sld

        return temp_sld

    def create_combobox(self, root, xpos: int, ypos: int, items, callback, opt_id=0) -> ttk.Combobox:
        temp_cbx = ttk.Combobox(root, values=items)
        temp_cbx.bind("<<ComboboxSelected>>", callback)
        temp_cbx.place(x=xpos, y=ypos, width=165)

        if opt_id != 0:
            self.elements[opt_id] = temp_cbx

        return temp_cbx

    def create_logbox(self, root, xpos: int, ypos: int, w: int, h: int, opt_id=0) -> tk.Text:
        temp_tbx = tk.Text(root, width=w, height=h)

        scroll_y = ttk.Scrollbar(temp_tbx)
        scroll_y.pack(side = tk.RIGHT, fill = 'both')#tk.Y)
        scroll_x = ttk.Scrollbar(temp_tbx, orient = tk.HORIZONTAL)
        scroll_x.pack(side = tk.BOTTOM, fill = 'both')#tk.X)

        scroll_y.config(command = temp_tbx.yview)
        scroll_x.config(command = temp_tbx.xview)

        temp_tbx.configure(
            font=self.log_font, wrap=tk.NONE, 
            yscrollcommand = scroll_y.set,
            xscrollcommand = scroll_x.set
        )

        temp_tbx.place(x=xpos, y=ypos, width=w, height=h)

        if opt_id != 0:
            self.elements[opt_id] = temp_tbx

        return temp_tbx

    def create_image(self, root, xpos: int, ypos: int, data, w: int, h: int, opt_id=0) -> tk.Label: # whatever
        if data == 0:
            temp_img = tk.PhotoImage(format='png', height=h, width=w)
        else:
            temp_img = tk.PhotoImage(data=data, format='png', height=h, width=w)

        temp_lbl = tk.Label(root, text='ICON', image=temp_img)
        temp_lbl.place(x=xpos, y=ypos)

        if opt_id != 0:
            self.elements[opt_id] = temp_lbl

        return temp_lbl

    def create_progressbar(self, root, xpos: int, ypos: int, w: int, h: int, opt_id=0) -> ttk.Progressbar:
        temp_pb = ttk.Progressbar(
            root, orient='horizontal',
            mode='indeterminate',
            length=self.w-330
        )

        temp_pb.place(x=xpos, y=ypos)
        
        if opt_id != 0:
            self.elements[opt_id] = temp_pb

        return temp_pb

    def create_tab_control(self, root, xpos: int, ypos: int, w: int, h: int, opt_id=0) -> ttk.Notebook:
        temp_tabbar = ttk.Notebook(root)
        temp_tabbar.place(x=xpos, y=ypos)

        if opt_id != 0:
            self.elements[opt_id] = temp_tabbar

        return temp_tabbar

    def create_tab(self, root, w: int, h: int, text: str, opt_id=0) -> ttk.Frame:
        temp_tab = ttk.Frame(root, width=w, height=h)
        root.add(temp_tab, text=text)
        # root.pack(expand=1, fill="both")

        if opt_id != 0:
            self.elements[opt_id] = temp_tab

        return temp_tab

    def create_link(self, root, xpos: int, ypos: int, url: str, callback, opt_id=0) -> ttk.Label:
        temp_lbl = ttk.Label(
            root, text=url, cursor="hand2", 
            foreground= "#00FFFF"
        )

        temp_lbl.bind("<Button-1>", callback)
        temp_lbl.place(x=xpos, y=ypos)

        if opt_id != 0:
            self.elements[opt_id] = temp_lbl

        return temp_lbl

    def create_terminal(self, root, xpos: int, ypos: int, w: int, h: int, callback, opt_id=0) -> tk.Text:
        temp_tbx = tk.Text(root, width=w, height=h)

        temp_tbx.configure(
            font=self.terminal_font, wrap=tk.NONE, 
            foreground="#a6e22e", background="black"
        )

        temp_tbx.bind('<Return>', callback)
        temp_tbx.place(x=xpos, y=ypos, width=w, height=h)

        if opt_id != 0:
            self.elements[opt_id] = temp_tbx

        return temp_tbx

    
    #def create_line(self, root, xpos: int, ypos: int, xposf: int, yposf: int, width: int, opt_id=0):
    #    temp_ln = Canvas(root).create_line(xpos, ypos, xposf, yposf, width=width, fill="white")
    #    if opt_id != 0:
    #        self.elements[opt_id] = temp_ln
        