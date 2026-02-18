#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import messagebox, font
import time
import threading
import math
import random
from collections import deque
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Callable, Dict, Any

class Config:
    APP_TITLE = "Simulador Ultimate Torre de Hanói"
    WIDTH = 1024
    HEIGHT = 768
    FPS = 60
    MIN_DISKS = 3
    MAX_DISKS = 10
    DEFAULT_DISKS = 5
    PEG_WIDTH = 20
    PEG_HEIGHT = 250
    BASE_HEIGHT = 40
    DISK_HEIGHT = 25
    MIN_DISK_WIDTH = 60
    MAX_DISK_WIDTH = 200
    ANIMATION_SPEED_SLOW = 2.0
    ANIMATION_SPEED_NORMAL = 1.0
    ANIMATION_SPEED_FAST = 0.2
    ANIMATION_SPEED_INSTANT = 0.0
    TEXTS = {
        "pt_br": {
            "window_title": "Simulador Ultimate Torre de Hanói - Python Edition",
            "start": "Iniciar Solução Recursiva",
            "reset": "Reiniciar Tabuleiro",
            "stop": "Parar Execução",
            "speed": "Velocidade:",
            "disks": "Nº Discos:",
            "moves": "Movimentos:",
            "status": "Status:",
            "ready": "Pronto",
            "running": "Executando...",
            "paused": "Pausado",
            "finished": "Concluído com Sucesso!",
            "error_invalid": "Movimento Inválido!",
            "theme": "Tema Visual",
            "logs": "Log de Execução",
            "auto_solve": "Resolver Automaticamente",
            "step_mode": "Modo Passo-a-Passo"
        }
    }
    LANG = "pt_br"

    @staticmethod
    def get_text(key: str) -> str:
        return Config.TEXTS[Config.LANG].get(key, key)


class Cores:
    DARK_BG = "#2E3440"
    DARK_PANEL = "#3B4252"
    DARK_ACCENT = "#88C0D0"
    DARK_TEXT = "#ECEFF4"
    DARK_PEG = "#4C566A"
    DARK_BASE = "#434C5E"
    DISK_COLORS = [
        "#BF616A", "#D08770", "#EBCB8B", "#A3BE8C", "#B48EAD",
        "#81A1C1", "#88C0D0", "#5E81AC", "#BF616A", "#D08770"
    ]
    SUCCESS = "#A3BE8C"
    ERROR = "#BF616A"
    WARNING = "#EBCB8B"
class Vector2D:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)

    def distance_to(self, other) -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def __repr__(self):
        return f"Vec2({self.x:.1f}, {self.y:.1f})"

class MathUtils:
    @staticmethod
    def lerp(start: float, end: float, t: float) -> float:
        return start + (end - start) * t

    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        return 4 * t * t * t if t < 0.5 else 1 - (-2 * t + 2)**3 / 2

    @staticmethod
    def get_disk_width(disk_index: int, total_disks: int) -> int:
        min_w = Config.MIN_DISK_WIDTH
        max_w = Config.MAX_DISK_WIDTH
        step = (max_w - min_w) / max(1, (total_disks - 1))
        return int(min_w + (disk_index * step))

class EventManager:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def emit(self, event_type: str, data: Any = None):
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Erro no evento {event_type}: {e}")

events = EventManager()
class Disk:
    def __init__(self, size_index: int, total_disks: int):
        self.id = size_index
        self.width = MathUtils.get_disk_width(size_index, total_disks)
        self.height = Config.DISK_HEIGHT
        self.color = Cores.DISK_COLORS[size_index % len(Cores.DISK_COLORS)]
        self.pos = Vector2D(0, 0)
        self.target_pos = Vector2D(0, 0)
        self.is_moving = False

    def __repr__(self):
        return f"Disk({self.id})"

class Peg:
    def __init__(self, peg_id: int, name: str, center_x: int, base_y: int):
        self.id = peg_id
        self.name = name
        self.center_x = center_x
        self.base_y = base_y
        self.disks: List[Disk] = []

    def push(self, disk: Disk) -> bool:
        if not self.disks or self.disks[-1].id > disk.id:
            self.disks.append(disk)
            self._update_disk_target(disk)
            return True
        return False

    def pop(self) -> Optional[Disk]:
        if self.disks:
            return self.disks.pop()
        return None

    def peek(self) -> Optional[Disk]:
        return self.disks[-1] if self.disks else None

    def is_empty(self) -> bool:
        return len(self.disks) == 0

    def _update_disk_target(self, disk: Disk):
        index_in_stack = len(self.disks) - 1
        target_y = self.base_y - (index_in_stack * Config.DISK_HEIGHT) - Config.BASE_HEIGHT
        disk.target_pos = Vector2D(self.center_x, target_y)

    def refresh_layout(self):
        for i, disk in enumerate(self.disks):
            target_y = self.base_y - (i * Config.DISK_HEIGHT) - Config.BASE_HEIGHT
            disk.target_pos = Vector2D(self.center_x, target_y)
            if not disk.is_moving:
                disk.pos = Vector2D(self.center_x, target_y)

class MoveCommand:
    def __init__(self, disk: Disk, source_peg: Peg, target_peg: Peg):
        self.disk = disk
        self.source = source_peg
        self.target = target_peg
        self.timestamp = time.time()

    def __str__(self):
        return f"Disco {self.disk.id + 1} de {self.source.name} para {self.target.name}"

class GameEngine:
    def __init__(self):
        self.num_disks = Config.DEFAULT_DISKS
        self.pegs: List[Peg] = []
        self.moves_history: List[MoveCommand] = []
        self.is_solving = False
        self.stop_requested = False
        self.move_count = 0
        
        self._setup_pegs()
        self.reset_game()

    def _setup_pegs(self):
        margin = Config.WIDTH // 4
        self.pegs = [
            Peg(0, "Origem (A)", margin, Config.HEIGHT - 100),
            Peg(1, "Auxiliar (B)", margin * 2, Config.HEIGHT - 100),
            Peg(2, "Destino (C)", margin * 3, Config.HEIGHT - 100)
        ]

    def reset_game(self, new_disk_count: int = None):
        if new_disk_count:
            self.num_disks = new_disk_count
        
        self.stop_requested = False
        self.is_solving = False
        self.move_count = 0
        self.moves_history.clear()

        for peg in self.pegs:
            peg.disks.clear()

        for i in range(self.num_disks - 1, -1, -1):
            disk = Disk(i, self.num_disks)
            self.pegs[0].push(disk)
            disk.pos = Vector2D(disk.target_pos.x, disk.target_pos.y)

        events.emit("reset")
        events.emit("log", f"Jogo reiniciado com {self.num_disks} discos.")

    def move_disk(self, source_idx: int, target_idx: int) -> bool:
        source_peg = self.pegs[source_idx]
        target_peg = self.pegs[target_idx]

        if source_peg.is_empty():
            events.emit("error", "Pino de origem vazio.")
            return False

        disk_to_move = source_peg.peek()
        top_target = target_peg.peek()
        if top_target and top_target.id < disk_to_move.id:
            events.emit("error", Config.get_text("error_invalid"))
            return False
        disk = source_peg.pop()
        target_peg.push(disk)
        cmd = MoveCommand(disk, source_peg, target_peg)
        self.moves_history.append(cmd)
        self.move_count += 1
        events.emit("move_start", cmd)
        if len(self.pegs[2].disks) == self.num_disks:
            events.emit("game_won")
        return True

    def update_peg_positions(self, width: int, height: int):
        part = width // 4
        base_y = height - 100
        self.pegs[0].center_x = part
        self.pegs[0].base_y = base_y
        self.pegs[1].center_x = part * 2
        self.pegs[1].base_y = base_y
        self.pegs[2].center_x = part * 3
        self.pegs[2].base_y = base_y
        
        for peg in self.pegs:
            peg.refresh_layout()

class HanoiSolver:
    def __init__(self, engine: GameEngine):
        self.engine = engine
        self.delay = Config.ANIMATION_SPEED_NORMAL
        self._thread: Optional[threading.Thread] = None

    def start_solving(self):
        if self.engine.is_solving:
            return
        if len(self.engine.pegs[2].disks) == self.engine.num_disks or self.engine.move_count > 0:
            self.engine.reset_game()

        self.engine.is_solving = True
        self.engine.stop_requested = False
        self._thread = threading.Thread(target=self._run_thread, daemon=True)
        self._thread.start()
        events.emit("status_change", Config.get_text("running"))

    def stop(self):
        self.engine.stop_requested = True
        self.engine.is_solving = False
        events.emit("status_change", "Parado pelo usuário")

    def set_speed(self, speed_val: float):
        self.delay = speed_val

    def _run_thread(self):
        start_time = time.time()
        try:
            self._recursive_move(self.engine.num_disks, 0, 2, 1)
            
            if not self.engine.stop_requested:
                total_time = time.time() - start_time
                events.emit("log", f"Solução concluída em {total_time:.2f}s")
                events.emit("status_change", Config.get_text("finished"))
        except Exception as e:
            events.emit("error", f"Erro na solução: {str(e)}")
        finally:
            self.engine.is_solving = False

    def _recursive_move(self, n: int, source: int, target: int, aux: int):
        if self.engine.stop_requested:
            return

        if n > 0:
            self._recursive_move(n - 1, source, aux, target)

            if self.engine.stop_requested: return
            time.sleep(self.delay)
            success = self.engine.move_disk(source, target)

            if not success:
                self.engine.stop_requested = True
                return
            self._recursive_move(n - 1, aux, target, source)

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

class GameRenderer(tk.Canvas):
    def __init__(self, parent, engine: GameEngine):
        super().__init__(parent, bg=Cores.DARK_BG, highlightthickness=0)
        self.engine = engine
        self.pack(fill="both", expand=True)
        self.animating_disks: List[Dict] = []
        self.bind("<Configure>", self.on_resize)
        self.running = True
        self._animate()

    def on_resize(self, event):
        self.engine.update_peg_positions(event.width, event.height)
        self.redraw()

    def _animate(self):
        if not self.running:
            return

        self.update_animations()
        self.redraw()
        self.after(int(1000/Config.FPS), self._animate)

    def start_disk_animation(self, disk: Disk, from_pos: Vector2D, to_pos: Vector2D, duration: float):
        top_y = 100
        
        p1 = from_pos
        p2 = Vector2D(from_pos.x, top_y)
        p3 = Vector2D(to_pos.x, top_y)
        p4 = to_pos
        
        disk.is_moving = True
        self.animating_disks.append({
            "disk": disk,
            "path": [p1, p2, p3, p4],
            "segment": 0,
            "t": 0.0,
            "speed": max(0.05, 1.0 / (duration * Config.FPS)) if duration > 0 else 1.0
        })

    def update_animations(self):
        finished_anims = []
        
        for anim in self.animating_disks:
            disk = anim["disk"]
            path = anim["path"]
            idx = anim["segment"]
            
            anim["t"] += anim["speed"]
            
            if anim["t"] >= 1.0:
                anim["t"] = 0.0
                anim["segment"] += 1
                if anim["segment"] >= len(path) - 1:
                    disk.pos = path[-1]
                    disk.is_moving = False
                    finished_anims.append(anim)
                    continue
            
            curr_start = path[anim["segment"]]
            curr_end = path[anim["segment"] + 1]
            
            t_val = anim["t"]
            if anim["segment"] == 1:
                pass
            else:
                t_val = MathUtils.ease_in_out_cubic(t_val)
                
            new_x = MathUtils.lerp(curr_start.x, curr_end.x, t_val)
            new_y = MathUtils.lerp(curr_start.y, curr_end.y, t_val)
            
            disk.pos = Vector2D(new_x, new_y)

        for a in finished_anims:
            self.animating_disks.remove(a)

    def redraw(self):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        
        base_y = Config.HEIGHT - 100 + Config.BASE_HEIGHT/2
        self.create_rectangle(50, self.engine.pegs[0].base_y, w-50, self.engine.pegs[0].base_y + 20, 
                              fill=Cores.DARK_BASE, outline="")

        for peg in self.engine.pegs:
            x1 = peg.center_x - Config.PEG_WIDTH // 2
            y1 = peg.base_y - Config.PEG_HEIGHT
            x2 = peg.center_x + Config.PEG_WIDTH // 2
            y2 = peg.base_y
            
            self.create_rectangle(x1, y1, x2, y2, fill=Cores.DARK_PEG, outline="")
            self.create_text(peg.center_x, y2 + 30, text=peg.name, fill=Cores.DARK_TEXT, font=("Arial", 12, "bold"))

        all_disks = []
        for peg in self.engine.pegs:
            all_disks.extend(peg.disks)
            
        for disk in all_disks:
            self._draw_disk(disk)

    def _draw_disk(self, disk: Disk):
        cx, cy = disk.pos.x, disk.pos.y
        w = disk.width
        h = disk.height
        
        x1 = cx - w // 2
        y1 = cy - h
        x2 = cx + w // 2
        y2 = cy
        
        self.create_rectangle(x1, y1, x2, y2, fill=disk.color, outline="#2E3440", width=1)
        self.create_line(x1+2, y1+2, x2-2, y1+2, fill="#E6E6E6") 
        self.create_text(cx, cy - h//2, text=str(disk.id + 1), fill="#2E3440", font=("Arial", 10, "bold"))

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
        
        lbl_title = tk.Label(header_frame, text="TOWER OF HANOI", font=("Helvetica", 24, "bold"), 
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

class IterativeSolver:
    @staticmethod
    def solve(n, source, target, aux):
        total_moves = 2**n - 1
        pass

class FrameStewartSolver:
    def __init__(self):
        self._memo = {}

    def solve(self, n_disks, k_pegs):
        if k_pegs < 3: return float('inf')
        if k_pegs == 3: return 2**n_disks - 1
        return 0

def main():
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    app = HanoiApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

if __name__ == "__main__":
    main()