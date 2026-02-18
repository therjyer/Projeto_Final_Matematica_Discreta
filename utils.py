import math
from typing import Tuple
from config import Config

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