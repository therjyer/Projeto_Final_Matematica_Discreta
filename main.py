#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import messagebox
import time

from config import Config, Cores
from events import events
from engine import GameEngine, HanoiSolver
from models import MoveCommand
from ui_components import RoundedPanel, ModernButton, StatBox
from renderer import GameRenderer

class HanoiApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title(Config.get_text("window_title"))
        self.geometry(f"{Config.WIDTH}x{Config.HEIGHT}")
        self.configure(bg=Cores.DARK_BG)
        self.minsize(800, 600)
        self.engine = GameEngine()
        self.solver = HanoiSolver(self.engine)
        self._setup_ui()
        self._bind_events()
        self.log("Sistema inicializado. Pronto.")

    def _setup_ui(self):
        header_frame = tk.Frame(self, bg=Cores.DARK_PANEL, height=80)
        header_frame.pack(side="top", fill="x")
        header_frame.pack_propagate(False)
        
        lbl_title = tk.Label(header_frame, text="TORRE DE HANÓI", font=("Helvetica", 24, "bold"), 
                             bg=Cores.DARK_PANEL, fg=Cores.DARK_TEXT)
        lbl_title.pack(side="left", padx=20)
        
        sidebar = tk.Frame(self, bg=Cores.DARK_BG, width=250)
        sidebar.pack(side="right", fill="y", padx=10, pady=10)

        ctrl_panel = RoundedPanel(sidebar, 230, 300, Cores.DARK_PANEL)
        ctrl_panel.pack(pady=10)

        sidebar_content = tk.Frame(sidebar, bg=Cores.DARK_BG)
        sidebar_content.place(x=0, y=0, relwidth=1, relheight=1)

        card_config = tk.Frame(sidebar_content, bg=Cores.DARK_PANEL, bd=0, padx=10, pady=10)
        card_config.pack(fill="x", pady=5)
        
        tk.Label(card_config, text="Configuração", font=("Arial", 10, "bold"), 
                 bg=Cores.DARK_PANEL, fg=Cores.DARK_ACCENT).pack(anchor="w")
        
        tk.Label(card_config, text=Config.get_text("disks"), bg=Cores.DARK_PANEL, fg="white").pack(anchor="w", pady=5)
        self.scale_disks = tk.Scale(card_config, from_=Config.MIN_DISKS, to_=Config.MAX_DISKS, 
                                    orient="horizontal", bg=Cores.DARK_PANEL, fg="white", 
                                    highlightthickness=0, command=self.on_disk_change)
        self.scale_disks.set(Config.DEFAULT_DISKS)
        self.scale_disks.pack(fill="x")
        
        tk.Label(card_config, text=Config.get_text("speed"), bg=Cores.DARK_PANEL, fg="white").pack(anchor="w", pady=5)
        self.scale_speed = tk.Scale(card_config, from_=1, to=10, orient="horizontal", 
                                    bg=Cores.DARK_PANEL, fg="white", highlightthickness=0,
                                    command=self.on_speed_change)
        self.scale_speed.set(5)
        self.scale_speed.pack(fill="x")
        
        btn_frame = tk.Frame(sidebar_content, bg=Cores.DARK_BG)
        btn_frame.pack(fill="x", pady=10)
        
        self.btn_solve = ModernButton(btn_frame, Config.get_text("start"), self.action_solve, width=230, bg_color="#5E81AC")
        self.btn_solve.pack(pady=5)
        
        self.btn_reset = ModernButton(btn_frame, Config.get_text("reset"), self.action_reset, width=230, bg_color="#BF616A")
        self.btn_reset.pack(pady=5)
        
        stats_frame = tk.Frame(sidebar_content, bg=Cores.DARK_PANEL, padx=10, pady=10)
        stats_frame.pack(fill="x", pady=10)
        
        self.stat_moves = StatBox(stats_frame, Config.get_text("moves"))
        self.stat_moves.pack(fill="x", pady=2)
        
        self.stat_min_moves = StatBox(stats_frame, "Mínimo (2^n - 1)")
        self.stat_min_moves.set_value(str(2**Config.DEFAULT_DISKS - 1))
        self.stat_min_moves.pack(fill="x", pady=2)
        
        self.lbl_status = tk.Label(stats_frame, text=Config.get_text("ready"), fg=Cores.DARK_ACCENT, bg=Cores.DARK_PANEL)
        self.lbl_status.pack(pady=10)

        log_label = tk.Label(sidebar_content, text=Config.get_text("logs"), bg=Cores.DARK_BG, fg="white")
        log_label.pack(anchor="w")
        
        self.log_box = tk.Listbox(sidebar_content, bg="#1d2129", fg="#00ff00", height=10, 
                                  bd=0, font=("Consolas", 8))
        self.log_box.pack(fill="both", expand=True)

        center_frame = tk.Frame(self, bg=Cores.DARK_BG)
        center_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        self.renderer = GameRenderer(center_frame, self.engine)

    def _bind_events(self):
        """Conecta eventos do EventManager aos métodos da UI."""
        events.subscribe("move_start", self.on_move_event)
        events.subscribe("reset", self.on_reset_event)
        events.subscribe("log", self.log)
        events.subscribe("status_change", self.update_status)
        events.subscribe("error", self.show_error)
        events.subscribe("game_won", lambda _: messagebox.showinfo("Vitória", "A torre foi completada!"))

    def on_disk_change(self, val):
        """Callback do slider de discos."""
        n = int(val)
        if not self.engine.is_solving:
            self.engine.reset_game(n)
            self.stat_min_moves.set_value(str(2**n - 1))
            self.renderer.redraw()

    def on_speed_change(self, val):
        v = int(val)
        factor = 11 - v
        delay = factor * 0.15
        self.solver.set_speed(delay)

    def action_solve(self):
        if self.engine.is_solving:
            self.solver.stop()
            self.btn_solve.delete("all")
            self.log("Parada solicitada...")
        else:
            self.solver.start_solving()
    
    def action_reset(self):
        self.solver.stop()
        self.after(100, lambda: self.engine.reset_game(self.engine.num_disks))
        self.renderer.redraw()

    def on_move_event(self, move_cmd: MoveCommand):
        self.stat_moves.set_value(self.engine.move_count)
        duration = self.solver.delay * 0.8 
        self.renderer.start_disk_animation(move_cmd.disk, move_cmd.disk.pos, move_cmd.disk.target_pos, duration)

    def on_reset_event(self, _):
        self.stat_moves.set_value(0)
        self.update_status(Config.get_text("ready"))
        self.renderer.redraw()

    def update_status(self, text):
        self.lbl_status.config(text=text)

    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        full_msg = f"[{timestamp}] {message}"
        self.log_box.insert(tk.END, full_msg)
        self.log_box.see(tk.END)
        print(full_msg)

    def show_error(self, msg):
        messagebox.showerror("Erro", msg)

    def on_closing(self):
        self.solver.stop()
        self.renderer.running = False
        self.destroy()

if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    app = HanoiApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()