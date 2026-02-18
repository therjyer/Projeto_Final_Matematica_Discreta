class Config:
    APP_TITLE = "Torre de Hanói"
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
            "window_title": "Torre de Hanói",
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