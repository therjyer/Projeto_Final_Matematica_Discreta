import time
from typing import List, Optional
from config import Config, Cores
from utils import Vector2D, MathUtils

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