" menus "
# pylint: disable=C0103
# I don't want to integrate tkinter with pygame, so i made my own tkinter for pygame
from __future__ import annotations
from typing import Optional
from functools import wraps as _wraps
import pygame
from pygame.locals import SRCALPHA, KEYDOWN, K_SPACE, QUIT, RLEACCEL, MOUSEMOTION, MOUSEBUTTONDOWN
import stuuf
import util
import time
import os.path
from settings import DEBUG, VERY_VERBOSE, GFX_MODE, scr_size, scr_w, scr_h
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

class Widget(pygame.sprite.Sprite):
    surf: pygame.Surface
    rect: pygame.Rect | pygame.FRect
    def __init__(self, size, pos=[0,0], **kwargs):
        super().__init__()
        self.pos_offset = kwargs.get('offset', (0,0))
        self.pos = pos
        self.size = size
        self.width, self.height = self.size # tuple unpacking!!!
        self.rect = pygame.rect.Rect(pos, size)
        self.font_size = kwargs.get('font_size', self.height - 8)
        self.font = pygame.font.Font(kwargs.get('font_id', None), self.font_size)
    def render(self, surf, pos: Optional=None):
        if pos is None and hasattr(self, 'rect'): pos = self.rect
        surf.blit(self.surf, pos)
    def is_mouseover(self, mousepos=None) -> bool:
        if mousepos is None: mousepos = util.sub_pos(pygame.mouse.get_pos(), self.pos_offset)
        return self.rect.collidepoint(mousepos)
    def set_hover(self, hovering: bool):
        pass
    def handle_click(self):
        return # weird
        """if self.is_mouseover():
            return True"""
class Button(Widget):
    img = pygame.image.load(os.path.join('assets', 'gui', 'button.png'))
    highlight = pygame.image.load(os.path.join('assets', 'gui', 'button_highlighted.png'))
    text: str = ''
    def __init__(self, size=[240,160], pos=[0,0], **kwargs):
        super().__init__(size, pos, **kwargs)
        self.set_text()
        self.onClick = lambda: None
    def set_text(self, text: Optional[str]=None):
        self.surf= pygame.transform.scale(self.img, self.size)
        if text is None: return # pass no args to reset surf
        self.text = text.upper()
        surf = self.font.render(self.text, True, (255,255,255), wraplength=self.width)
        rect = surf.get_rect(centerx=self.size[0]//2, centery=self.size[1]//2)
        self.surf.blit(surf, rect)
    def is_mouseover(self, mousepos=None) -> bool:
        if mousepos is None: mousepos = util.sub_pos(pygame.mouse.get_pos(), self.pos_offset)
        return self.rect.collidepoint(mousepos)
    def set_hover(self, hovering: bool):
        self.set_text(self.text)
        if hovering: self.surf.blit(pygame.transform.scale(self.highlight, self.size), (0,0))
    def handle_click(self):
        if self.is_mouseover():
            self.onClick()
class Label(Widget):
    " BROKEN DO NOT USE CAUSES PYTHON TO EXIT FROM SIGABRT IDK WHY "
    def __init__(self, size, pos=[0,0], **kwargs):
        kwargs['font_size'] = kwargs.get('font_size', int(size[1] / 2))
        super().__init__(size, pos, **kwargs)
        self.surf = pygame.Surface(size, SRCALPHA)
    def set_text(self, text):
        self.text = text.upper()
        txt = self.text.split('\n')
        surfs = [self.font.render(t, True, (255,255,255), wraplength=self.width) \
                              for t in txt]
        surf  = pygame.Surface([max(s.width for s in surfs),
                                self.font_size*len(txt)]).convert_alpha()
        for i, s in enumerate(surfs):
            surf.blit(s, (0,self.font_size*i))
        rect = surf.get_rect(centerx=self.size[0]//2, centery=self.size[1]//2)
        self.surf.blit(surf, rect)
class ImageLabel(Widget):
    def __init__(self, size, pos=[0,0], **kwargs):
        super().__init__(size, pos, **kwargs)
        self.surf = pygame.Surface(size, SRCALPHA)
    def load_texture(self, texture):
        self.surf.blit(
            pygame.transform.scale(
                pygame.image.load(
                    os.path.join('assets', 'gui', texture)),
                self.size),
            (0,0))

class Window(pygame.Surface):
    _events: list[pygame.event.Event]
    _eventhandlers: dict[int, list]
    do_event_handlers: bool = True
    events_since_render: int = 0
    def __init__(self, size=scr_size, surf_flags=0, **kwargs):
        super().__init__(size, surf_flags | SRCALPHA)
        self._eventhandlers = {}
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
        if event.type not in self._eventhandlers: return # is no handlers are registered
        for eventhandler in self._eventhandlers[event.type]:
            eventhandler(event)
        self.events_since_render += 1
    def get_events(self) -> list[pygame.event.Event]:
        """works the same as pygame.event.get but only gets events passed to process_event
        also it won't interfere with the global pygame.event.get"""
        events = self._events.copy()
        self._events.clear()
        return events
    def register_event_handler(self, eventId: int, function):
        if eventId not in self._eventhandlers: self._eventhandlers[eventId] = []
        self._eventhandlers[eventId].append(function)

class BaseMenu(Window):
    write_surf: pygame.Surface
    widgets: pygame.sprite.Group
    visible: bool
    background_transparency: int = 0
    submenus: list[BaseMenu]
    def __init__(self, size=scr_size, surf_flags=0, **kwargs):
        super().__init__(size, surf_flags, **kwargs)
        if VERY_VERBOSE: print("\033[36mInitialising Menu", repr(self), '\033[0m')
        self.visible = kwargs.get('visible', True)
        self.write_rect = pygame.rect.Rect(self.left_margin, self.top_margin,
                               scr_w - self.left_margin*2, scr_h - self.top_margin*2)
        self.write_surf = pygame.Surface((self.write_rect.width,
                                          self.write_rect.height), surf_flags | SRCALPHA)
        self.widgets = pygame.sprite.Group()
        self.submenus= []
        self.register_event_handler(MOUSEMOTION, self.mousemove_handler)
        self.register_event_handler(MOUSEBUTTONDOWN, self.mousedown_handler)
    def mousemove_handler(self, event: pygame.event.Event):
        # update button stuff
        for widget in self.widgets:
            if isinstance(widget, Button):
                widget.set_hover(widget.is_mouseover())
    def mousedown_handler(self, event: pygame.event.Event):
        # update button stuff
        for widget in self.widgets:
            widget.handle_click()
    def update_gfx(self):
        self.do_event_handlers = self.visible
        if self.events_since_render == 0: return
        self.events_since_render = 0
        # clear self (screen)
        if not self.visible: self.fill((0,0,0,0)); return
        self.fill((0,0,0,self.background_transparency))
        # render widgets
        for widget in self.widgets:
            widget.render(self.write_surf)
            #if VERY_VERBOSE and GFX_MODE > 3:
            #    pygame.draw.rect(self, (200,200,200), widget.rect, 2)
                #pygame.draw.circle(self, (255,255,255), util.sub_pos(pygame.mouse.get_pos(), widget.pos_offset), 4)
        # render to main surf
        self.blit(self.write_surf, self.write_rect)
        # render submenus on top
        for submenu in self.submenus:
            if submenu.visible:
                for event in self.get_events():
                    submenu.process_event(event)
            submenu.update_gfx()
            self.blit(submenu, (0,0))
        #if VERY_VERBOSE: pygame.draw.rect(self, (100, 100, 100), self.write_rect, 3)

class MainMenu(BaseMenu):
    left_margin = 0 + MAINMENU_MARGIN_X
    right_margin = scr_w - MAINMENU_MARGIN_X
    top_margin = 0 + MAINMENU_MARGIN_Y
    bottom_margin = scr_h - MAINMENU_MARGIN_Y
    def build_contents(self):
        rusure = AreYouSure(visible=False)
        rusure.build_contents(function=lambda: pygame.event.post(pygame.event.Event(QUIT)))
        self.submenus.append(rusure)
        if VERY_VERBOSE: print("\033[36mMainMenu safe area rect:", self.write_rect, '\033[0m')
        #self.write_surf.fill((255,255,255)) # placeholder white square
        back_button = Button([self.write_rect.width, 96], offset=self.write_rect.topleft)
        back_button.set_text("Return to Game")
        back_button.onClick = lambda: pygame.event.post(pygame.event.Event(KEYDOWN, key=K_SPACE))
        self.widgets.add(back_button)
        quit_button = Button([self.write_rect.width,96], [0,self.write_rect.bottom-192],offset=self.write_rect.topleft)
        quit_button.onClick = lambda: setattr(rusure, 'visible', True)
        quit_button.set_text("Quit Game")
        self.widgets.add(quit_button)
class AreYouSure(BaseMenu):
    left_margin = 0 + 300 #      # margins
    right_margin = scr_w - 300 # # and
    top_margin = 0 + 250 #       # stuff
    bottom_margin = scr_h - 250
    background_transparency = 200
    def build_contents(self, function):
        label = ImageLabel([self.write_rect.width, self.write_rect.height//2],
                       [0,0],
                       offset=self.write_rect.topleft)
        if VERY_VERBOSE: print("\033[36mRUSure.size=", label.size, "\033[0m")
        label.load_texture('rusure.png')
        no_button = Button([self.write_rect.width//2, self.write_rect.height//2],
                               [0, self.write_rect.height//2], offset=self.write_rect.topleft)
        no_button.set_text("No")
        yes_button= Button([self.write_rect.width//2, self.write_rect.height//2],
                               [self.write_rect.width//2, self.write_rect.height//2],
                               offset=self.write_rect.topleft)
        yes_button.set_text("Yes")
        no_button.onClick = lambda: setattr(self, 'visible', False) # fun little hack (setattr to avoid setting variables in lambda)
        def onYes(): self.visible = True; function() # could use same hack here (turns out that said hack is less efficient but whatever i like lambdas)
        yes_button.onClick = onYes
        self.widgets.add(yes_button, no_button, label)

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
        for i, line in enumerate(self.flags.profiler.export_report().split('\n')):
            self.renderText(line, 7+i)
        #self.renderText("Flags:", 1)
        #self.renderText(repr(self.flags), 2)
        self.renderText(HatEventType.toString(self.hatevent), self.lines-1)
    def log_hatevent(self, hatevent: int):
        "log a hatevent to show at the bottom of the window"
        self.hatevent = hatevent

def wait_for_event(): pass
def _wait_for_event():
    while 1:
        if pygame.event.peek(MOUSEMOTION): return
        if pygame.event.peek(MOUSEBUTTONDOWN): return
        if pygame.event.peek(KEYDOWN): return
        time.sleep(0.05)
        pygame.display.flip()
