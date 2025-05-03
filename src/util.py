from __future__ import annotations

from typing import Union
from pygame.math import Vector2
#from sprites import TinaFey

TinaFey = object

class TinaContainer:
    tina: Union[TinaFey, Ellipsis]
    def __init__(self, tina: Union[TinaFey, Ellipsis]=Ellipsis) -> None:
        self.tina = tina
    def set_tina(self, tina) -> TinaFey:
        self.tina = tina
        return self.tina
    def set_null_tina(self) -> Ellipsis:
        self.tina = Ellipsis
        return self.tina
    def get_tina(self) -> Union[TinaFey, Ellipsis]:
        return self.tina
    def has_tina(self) -> bool:
        return self.tina is not Ellipsis

def add_pos(x, y):
    x = Vector2(x)
    y = Vector2(y)
    z = x + y
    return [z.x, z.y]
def sub_pos(x, y):
    x = Vector2(x)
    y = Vector2(y)
    z = x - y
    return [z.x, z.y]