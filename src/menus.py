" menus "
# pylint: disable=C0103
from functools import wraps as _wraps
import pygame
from pygame.locals import SRCALPHA, KEYDOWN, K_SPACE
import stuuf, util
import os.path
from settings import DEBUG, VERY_VERBOSE, scr_size, scr_w, scr_h
from effect import get_hatranksupto, HatEventType

pygame.font.init()

MAINMENU_MARGIN_X = 96
MAINMENU_MARGIN_Y = 64

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

darkener = pygame.Surface(scr_size, SRCALPHA)
darkener.fill((15,16,18,50))

class Widget:
    surf: pygame.Surface
    def render(self, surf, pos):
        surf.blit(self.surf, pos)
class BaseButton(Widget):
    img = pygame.image.load(os.path.join('assets', 'gui', 'button.png'))
    highlight = pygame.image.load(os.path.join('assets', 'gui', 'button_highlighted.png'))
    text: str = ''
    def __init__(self, size=[240,160], pos=[0,0], **kwargs):
        super().__init__()
        self.pos_offset = kwargs.get('offset', (0,0))
        self.size = size
        self.rect = pygame.rect.Rect(pos, size)
        self.font_size = kwargs.get('font_size', 24)
        self.font = pygame.font.Font(kwargs.get('font_id', None), self.font_size)
        self.set_text()
    def set_text(self, text: str=None):
        self.surf= pygame.transform.scale(self.img, self.size)
        if text is None: return # pass no args to reset surf
        self.text = text
        surf = self.font.render(text, True, (0,1,2), wraplength=self.width)
        rect = surf.get_rect(centerx=self.size[0]//2, centery=self.size[1]//2)
        self.surf.blit(surf, rect)
    def is_mouseover(self, mousepos=None) -> bool:
        if mousepos is None: mousepos = util.add_pos(pygame.mouse.get_pos(), self.pos_offset)
        return self.rect.collidepoint(mousepos)
    def set_hover(self, hovering: bool):
        self.set_text(self.text)
        if hovering: self.surf.blit(self.highlight, (0,0))
    def handle_click(self):
        if self.is_mouseover():
            self.onClick()

class Window(pygame.Surface):
    _events: list[pygame.event.Event]
    def __init__(self, size=scr_size, surf_flags=0, **kwargs):
        super().__init__(size, surf_flags | SRCALPHA)
        self.font_size = kwargs.get('font_size', 24)
        self.font = pygame.font.Font(kwargs.get('font_id', None), self.font_size)
        self.lines= self.height // self.font_size
        self._events = []
    def renderText(self, text: str, line: int=0):
        "render text to at line"
        pos = [10, 8 + self.font_size*line]
        surf = self.font.render(text, True, (0,1,2), wraplength=self.width)
        return self.blit(surf, pos)
    def process_event(self, event: pygame.event.Event):
        "process events. used for the mouse and stuff"
        self._events.append(event)
    def get_events(self) -> list[pygame.event.Event]:
        """works the same as pygame.event.get but only gets events passed to process_event
        also it won't interfere with the global pygame.event.get"""
        events = self._events.copy()
        self._events.clear()
        return events

class MainMenu(Window):
    left_margin = 0 + MAINMENU_MARGIN_X
    right_margin = scr_w - MAINMENU_MARGIN_X
    top_margin = 0 + MAINMENU_MARGIN_Y
    bottom_margin = scr_h - MAINMENU_MARGIN_Y
    write_rect = pygame.rect.Rect(left_margin, top_margin,
                                  scr_w - MAINMENU_MARGIN_X*2, scr_h - MAINMENU_MARGIN_Y*2)
    write_surf = pygame.Surface((write_rect.width, write_rect.height))
    widgets: pygame.sprite.Group
    def _init__(self, size=scr_size, surf_flags=0, **kwargs):
        super().__init__(size, surf_flags, **kwargs)
        self.widgets = pygame.sprite.Group()
    def build_contents(self):
        if VERY_VERBOSE: print("MainMenu safe area rect:", self.write_ryect)
        #self.write_surf.fill((255,255,255)) # placeholder white square
        back_button = BaseButton([self.write_rect.width, 96])
        back_button.onclick = lambda s: pygame.event.post(pygame.event.Event(KEYDOWN, key=K_SPACE))
        self.widgets.add(back_button)
    def update_gfx(self):
        # update button stuff
        for widget in self.widgets:
            if isinstance(widget, BaseButton):
                widget.set_hover(widget.is_mouseover())
        # render widgets
        for widget in self.widgets:
            widget.render(self.write_rect)
        # render to main surf
        self.fill((0,0,0,0))
        self.blit(self.write_surf, self.write_rect)

class DebugWindow(Window):
    """debug window which inherits from pygame.Surface .
    call update every frame (or tick) and log_hatevent to log hatevents"""

    # subclasses can override the update method to show whatever info
    hatevent: int = 0
    def __init__(self, flags: stuuf.Flags, size=(300,400), *, surf_flags=0, **kwargs):
        super().__init__(size, surf_flags | SRCALPHA)
        self.flags = flags
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
        self.renderText(f"Current Level.passed: {self.flags.levels[self.flags.level].passed}", 6)
        #self.renderText("Flags:", 1)
        #self.renderText(repr(self.flags), 2)
        self.renderText(HatEventType.toString(self.hatevent), self.lines-1)
    def log_hatevent(self, hatevent: int):
        "log a hatevent to show at the bottom of the window"
        self.hatevent = hatevent
