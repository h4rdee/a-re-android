import tkinter as tk
import tkinter.font as tkFont

from tkinter import Canvas, ttk
from typing import Any

from logger import g_logger

from enum import IntEnum

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

        self.w = width
        self.h = height
        self.log_font = tkFont.Font(family="Helvetica", size=10)

    def get_element_by_opt_id(self, opt_id) -> Any:
        el = self.elements.get(opt_id)
        if el is None:
            g_logger.error(f"[!] element with opt_id {opt_id} not found\n")
        return el

    def push_external_element(self, element, id: int) -> None:
        if id != 0:
            self.elements[id] = element
        else:
            g_logger.warning(
                "[!] skipping element: external elements must have an id\n"
            )

    def create_button(self, root, xpos: int, ypos: int, label: str, callback, width=72, height=30, opt_id=0) -> None:
        temp_btn = ttk.Button(root, text=label, command=callback)
        temp_btn.place(x=xpos, y=ypos, width=width, height=height)
        if opt_id != 0:
            self.elements[opt_id] = temp_btn

    def create_label(self, root, xpos: int, ypos: int, label: str, opt_id=0) -> None:
        temp_lbl = ttk.Label(root, text=label)
        temp_lbl.place(x=xpos, y=ypos)
        if opt_id != 0:
            self.elements[opt_id] = temp_lbl

    def create_editbox(self, root, xpos: int, ypos: int, var: str, opt_id=0) -> None:
        temp_ebx = ttk.Entry(root)
        temp_ebx.insert(0, var)
        temp_ebx.place(x=xpos, y=ypos, width=70, height=30)
        if opt_id != 0:
            self.elements[opt_id] = temp_ebx

    def create_slider(self, root, xpos: int, ypos: int,
        min: float, max: float, orient: str, callback, opt_id=0) -> None:

        temp_sld = ttk.Scale(
            root, command=callback, 
            from_=min, to=max, orient=orient, 
        )
        temp_sld.place(x=xpos, y=ypos, height=150)
        if opt_id != 0:
            self.elements[opt_id] = temp_sld

    def create_combobox(self, root, xpos: int, ypos: int, items, callback, opt_id=0) -> None:
        temp_cbx = ttk.Combobox(root, values=items)
        temp_cbx.place(x=xpos, y=ypos, width=165)
        if opt_id != 0:
            self.elements[opt_id] = temp_cbx

    def create_logbox(self, root, xpos: int, ypos: int, w: int, h: int, opt_id=0) -> None:
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

    def create_image(self, root, xpos: int, ypos: int, data, w: int, h: int, opt_id=0) -> None:
        if data == 0:
            temp_img = tk.PhotoImage(format='png', height=h, width=w)
        else:
            temp_img = tk.PhotoImage(data=data, format='png', height=h, width=w)

        temp_lbl = tk.Label(root, text='ICON', image=temp_img)
        temp_lbl.place(x=xpos, y=ypos)

        if opt_id != 0:
            self.elements[opt_id] = temp_lbl

    def create_progressbar(self, root, xpos: int, ypos: int, w: int, h: int, opt_id=0) -> None:
        temp_pb = ttk.Progressbar(
            root, orient='horizontal',
            mode='indeterminate',
            length=self.w+10
        )
        temp_pb.place(x=xpos, y=ypos)
        
        if opt_id != 0:
            self.elements[opt_id] = temp_pb
    
    #def create_line(self, root, xpos: int, ypos: int, xposf: int, yposf: int, width: int, opt_id=0):
    #    temp_ln = Canvas(root).create_line(xpos, ypos, xposf, yposf, width=width, fill="white")
    #    if opt_id != 0:
    #        self.elements[opt_id] = temp_ln
        