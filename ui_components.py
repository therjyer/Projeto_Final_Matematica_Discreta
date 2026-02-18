import tkinter as tk
from config import Cores

class RoundedPanel(tk.Canvas):
    def __init__(self, parent, width, height, bg_color, radius=15, **kwargs):
        super().__init__(parent, width=width, height=height, bg=parent['bg'], highlightthickness=0, **kwargs)
        self.bg_color = bg_color
        self.radius = radius
        self.width = width
        self.height = height
        self.draw()

    def draw(self):
        self.delete("all")
        r = self.radius
        w, h = self.width, self.height
        c = self.bg_color
        
        self.create_arc(0, 0, 2*r, 2*r, start=90, extent=90, fill=c, outline=c)
        self.create_arc(w-2*r, 0, w, 2*r, start=0, extent=90, fill=c, outline=c)
        self.create_arc(0, h-2*r, 2*r, h, start=180, extent=90, fill=c, outline=c)
        self.create_arc(w-2*r, h-2*r, w, h, start=270, extent=90, fill=c, outline=c)
        self.create_rectangle(r, 0, w-r, h, fill=c, outline=c)
        self.create_rectangle(0, r, w, h-r, fill=c, outline=c)

class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command, width=120, height=40, bg_color="#4C566A", hover_color="#5E81AC"):
        super().__init__(parent, width=width, height=height, bg=parent['bg'], highlightthickness=0)
        self.command = command
        self.text = text
        self.bg_normal = bg_color
        self.bg_hover = hover_color
        self.w = width
        self.h = height
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.draw(self.bg_normal)

    def draw(self, color, offset=0):
        self.delete("all")
        self.create_rectangle(2, 2, self.w, self.h, fill="#2E3440", outline="")
        if offset > 0:
            self.create_rectangle(2, 2, self.w, self.h, fill=color, outline="")
        else:
            self.create_rectangle(0, 0, self.w-2, self.h-2, fill=color, outline="")
        text_x = self.w // 2 + (1 if offset else -1)
        text_y = self.h // 2 + (1 if offset else -1)
        self.create_text(text_x, text_y, text=self.text, fill="white", 
                         font=("Helvetica", 10, "bold"))

    def on_enter(self, e):
        self.draw(self.bg_hover)

    def on_leave(self, e):
        self.draw(self.bg_normal)

    def on_click(self, e):
        self.draw(self.bg_hover, offset=2)

    def on_release(self, e):
        self.draw(self.bg_hover)
        if self.command:
            self.command()

class StatBox(tk.Frame):
    def __init__(self, parent, title, value="0"):
        super().__init__(parent, bg=Cores.DARK_PANEL)
        self.lbl_title = tk.Label(self, text=title, font=("Arial", 8), bg=Cores.DARK_PANEL, fg="#D8DEE9")
        self.lbl_title.pack(anchor="w")
        self.lbl_value = tk.Label(self, text=value, font=("Arial", 14, "bold"), bg=Cores.DARK_PANEL, fg=Cores.DARK_ACCENT)
        self.lbl_value.pack(anchor="w")

    def set_value(self, val):
        self.lbl_value.config(text=str(val))