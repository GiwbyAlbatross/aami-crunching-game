" debug routines "
# pylint: disable=C0103
from functools import wraps as _wraps
import pygame
from pygame.locals import SRCALPHA
import stuuf
from settings import DEBUG, VERY_VERBOSE
from effect import get_hatranksupto, HatEventType

def debug(func):
    "decorator to make function only run if DEBUG is true"
    @_wraps(func)
    def rapper(*args, **kwargs):
        if DEBUG: return func(*args, **kwargs)
        # return None otherwise
def very_verbose(func):
    "decorator to make function only run if VERY_VERBOSE is true"
    @_wraps(func)
    def rapper(*args, **kwargs):
        if VERY_VERBOSE:
            return func(*args, **kwargs)
        # return None otherwise

class DebugWindow(pygame.Surface):
    """debug window which inherits from pygame.Surface .
    call update every frame (or tick) and  log_hatevent to log hatevents"""

    # subclasses can override the update method to show whatever info
    hatevent: int = 0
    def __init__(self, flags: stuuf.Flags, size=(300,400), *, surf_flags=0, **kwargs):
        super().__init__(size, surf_flags | SRCALPHA)
        self.flags = flags
        self.font_size = kwargs.get('font_size', 24)
        self.font = pygame.font.Font(kwargs.get('font_id', None), self.font_size)
        self.lines= self.height // self.font_size
    def renderText(self, text: str, line: int=0):
        "render text to at line"
        pos = [10, 8 + self.font_size*line]
        surf = self.font.render(text, True, (0,1,2), wraplength=self.width)
        return self.blit(surf, pos)
    def clear(self):
        "fill surf with default background colour"
        self.fill((250, 240, 200, 192))
    def update(self):
        "display the debug text this is supposed to show"
        self.clear()
        self.renderText(f"HatranksUpto: {get_hatranksupto()}", 0)
        self.renderText("Tina present." if self.flags.tinatainer.has_tina() else "No Tina", 1)
        try: self.renderText(repr(self.flags.player.effects[-1]), 2)
        except IndexError: self.renderText('No status effects', 2)
        self.renderText(f"Number of status effects: {len(self.flags.player.effects)}", 3)
        self.renderText(f"Number of doordack orders: {len(self.flags.doordack_orders)}", 4)
        self.renderText(f"Level: {self.flags.level}", 5)
        #self.renderText("Flags:", 1)
        #self.renderText(repr(self.flags), 2)
        self.renderText(HatEventType.toString(self.hatevent), self.lines-1)
    def log_hatevent(self, hatevent: int):
        "log a hatevent to show at the bottom of the window"
        self.hatevent = hatevent
