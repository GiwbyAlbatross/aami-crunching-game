" debug routines "
import pygame
import stuuf
from functools import wraps as _wraps
from settings import DEBUG, VERY_VERBOSE
from effect import get_hatranksupto, HatEventType

def debug(func):
    @_wraps(func)
    def rapper(*args, **kwargs):
        if DEBUG: return func(*args, **kwargs)
        else: return None
def very_verbose(func):
    @_wraps(func)
    def rapper(*args, **kwargs):
        if VERY_VERBOSE:
            return func(*args, **kwargs)
        elif DEBUG: return None 
        else: return None 

class DebugWindow(pygame.Surface):
    hatevent: int = 0
    def __init__(self, flags: stuuf.Flags, size=(300,400), *, surf_flags=0,**kwargs):
        super().__init__(size, surf_flags | pygame.SRCALPHA)
        self.flags = flags
        self.font_size = kwargs.get('font_size', 24)
        self.font = pygame.font.Font(kwargs.get('font_id', None), self.font_size)
        self.lines= self.height // self.font_size
    def renderText(self, text: str, line: int=0):
        pos = [10, 8 + self.font_size*line]
        surf = self.font.render(text, True, (0,1,2), wraplength=self.width)
        return self.blit(surf, pos)
    def clear(self):
        self.fill((250, 240, 200, 192))
    def update(self):
        self.clear()
        self.renderText(f"HatranksUpto: {get_hatranksupto()}", 0)
        self.renderText("Flags:", 1)
        self.renderText(repr(self.flags), 2)
        self.renderText(HatEventType.toString(self.hatevent), self.lines-1)
    def log_hatevent(self, hatevent: int):
        self.hatevent = hatevent