import time
import threading
from typing import List, Optional
from config import Config
from utils import Vector2D
from events import events
from models import Peg, Disk, MoveCommand

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