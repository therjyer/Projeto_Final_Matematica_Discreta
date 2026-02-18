from typing import Dict, List, Callable, Any

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

# Instância global compartilhada
events = EventManager()