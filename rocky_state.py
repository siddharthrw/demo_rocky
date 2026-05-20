from dataclasses import dataclass
from typing import Literal

@dataclass
class RockyState:
    x: float = 100.0
    direction: Literal["left", "right"] = "right"
    mood: Literal["walk", "stand", "type", "celebrate"] = "walk"
    chat_visible: bool = False
    speech: str = ""
    speech_timer: int = 0
    busy: bool = False
    stop_requested: bool = False