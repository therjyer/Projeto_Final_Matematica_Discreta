import tkinter as tk
from typing import List, Dict
from config import Config, Cores
from utils import Vector2D, MathUtils
from models import Disk
from engine import GameEngine

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