"a status effect system"
from __future__ import annotations

# pylint: disable=C0103

import random
import math

import pygame

import stuuf
import sprites
import util

from settings import VERY_VERBOSE, DEBUG, HARDNESS

class Effect:
    " base class for status effects "
    # class/static attributes
    associated_hat_id: str = 'null'
    name: str = 'aamicrunching.effect.base'
    bubble_colour: pygame.Color = pygame.Color(0,0,0)
    # instance/object attributes
    currently_on: sprites.Entity
    level: int
    def __init__(self, entity: sprites.Entity, level: int=1, **unused): # pylint: disable=W0613
        self.currently_on = entity
        self.level = max(1, level) # minimum effect level is 1, 0 would do nothing
    def apply_once(self):
        "one-off modify the properties of self.entity"
        pass
    def apply_on_tick(self):
        "modify the properties of self.entity, every tick"
        #self.apply_once() # [DONE] come up with better way to do that
        pass
    def __repr__(self) -> str:
        return f'<Effect {self.name}, level {self.level}>'
class Speed(Effect):
    " makes you run faster! (not snake oil) "
    name: str = 'speed'
    associated_hat_id: str = 'fiery-hat'
    
    def apply_once(self):
        "one-off modify the properties of self.entity"
        self.currently_on.speed = random.gauss(5 + self.level, 0.5)

class Repulsiveness(Effect):
    " repells tinas "
    name: str = 'repulsiveness'
    tina: sprites.TinaFey
    tinas: pygame.sprite.Group
    def __init__(self, entity: sprites.Entity,
                 level: int,
                 tina: util.TinaContainer,
                 tinas: pygame.sprite.Group=..., **unused):
        super().__init__(entity, level)
        self.tina = tina
        self.tinas = tinas
    def _apply_to_tina(self, tina: sprites.TinaFey):
        try:
            user = self.currently_on
            try: away_mv = pygame.Vector2(tina.rect.centerx - user.rect.centerx,
                                          tina.rect.centerx - user.rect.centerx).normalize()
            except ValueError: away_mv = pygame.Vector2()
            away_mv *= (self.level * 3)
            tina.mv += away_mv
        except AttributeError: pass
    def apply_on_tick(self):
        "repell tinas"
        tina = self.tina.get_tina()
        self._apply_to_tina(tina)
        for other_tina in self.tinas:
            self._apply_to_tina(other_tina)
class BaseAAMIAtrractor(Effect):
    aamis: pygame.sprite.Group
    def __init__(self, entity: sprites.Entity,
                 level: int,
                 aamis: pygame.sprite.Group=..., **unused):
        super().__init__(entity, level)
        self.aamis = aamis
    def _apply_to_aami(self, aami: sprites.AAMI):
        ### NEEDS WORK ##
        try:
            user = self.currently_on
            try: toward_mv = pygame.Vector2(user.rect.centerx - aami.rect.centerx,
                                            user.rect.centerx - aami.rect.centerx).normalize()
            except ValueError: toward_mv = pygame.Vector2()
            toward_mv *= self.level / 10
            aami.mv += toward_mv
        except AttributeError: pass
    def apply_on_tick(self):
        "attract aamis"
        for aami in self.aamis:
            self._apply_to_aami(aami)
class Attractiveness(BaseAAMIAtrractor):
    name: str = 'attractiveness'
    associated_hat: str = 'spotty'
class Levitation(Effect):
    name: str = 'levitiation'
    associated_hat: str = 'top'
    y: float
    def apply_once(self):
        self.y = self.currently_on.rect.centery
    def apply_on_tick(self):
        self.currently_on.rect.centery -= self.level * 1.5

effects: dict = {'repulsiveness':Repulsiveness, 'speed':Speed, 'attractiveness':Attractiveness, 'levitation':Levitation}
effectByHat: dict = {'fiery-hat':Speed, 'repulsive-hat':Repulsiveness, 'spotty':Attractiveness, 'top':Levitation, 'top-hat_grey':Levitation}

hatByRank: list = ['basic', 'top', 'spotty', 'repulsive-hat', 'fiery-hat', 'wizardry'] # so -1 is wizardy as well
hatranks_upto = 0.003 # starting value

def rand_lower() -> float:
    """a very poor attempt to generate random number that tend toward lower numbers.
    Not really the best, I need a better way to do this"""
    a = random.random()
    return (abs(2/(a-2)) - 0.5) * 2

def add_effect_from_hat(entity: sprites.Entity, hat: sprites.Hat, **kwargs) -> Effect:
    "add an effect to entity based on hat. kwargs are passed to the Effect constructor"
    args: dict = kwargs.copy() # nessesary? probably not
    args['level'] = int((hatranks_upto % 1) * 5)
    args['entity']= entity
    
    try:
        effect_constructor = effectByHat[hat.hatId]
        
        effect = effect_constructor(**args) # should perhaps be called kwargs, kwds or kws but whatever
        
        try:
            if VERY_VERBOSE: print(f"Removing status effect: {entity.effects[0]!r}")
            entity.effects = entity.effects[1:] # remove older effects
        except IndexError:
            if HARDNESS > 3: entity.effects = []
        if VERY_VERBOSE: print(f"Adding status effect: {effect!r}")
        entity.effects.append(effect)
    except KeyError:
        return Effect(entity) # base effect is basically a dud effect which does nothing
    else:
        return effect

def get_hat(**kwargs) -> tuple[sprites.Hat, int]:
    "select a hat based on internal module variables. Returns a tuple (Hat, hatevent)"
    v = math.floor(random.gauss(hatranks_upto, hatranks_upto / 5) + rand_lower()/10) % len(hatByRank)
    hatId = hatByRank[v]
    hateventlevel = 0
    if v < math.floor(hatranks_upto):
        hateventlevel = 1
    elif v == math.floor(hatranks_upto):
        hateventlevel = 2
    elif v > math.floor(hatranks_upto):
        hateventlevel = 3
    return sprites.Hat(hat_id=hatId, **kwargs), HatEventType.ADD_HAT | hateventlevel

def get_hatranksupto() -> float:
    "get the value of the internal hatranks_upto variable"
    return hatranks_upto

def process_aquire_hat(hat: sprites.Hat) -> int:
    "process the aquisision of hat"
    rank = hatByRank.index(hat.hatId)
    currentrank = math.floor(hatranks_upto)
    
    if rank == currentrank:
        return HatEventType.CATCH_AT
    if rank < currentrank:
        return HatEventType.CATCH_BEL
    if rank > currentrank:
        return HatEventType.CATCH_ABO
    else: return HatEventType.CATCH_HAT

def process_hat_event(event_type: int) -> None:
    "process a hatevent event_type. Used to update internal module values based on the hat event"
    global hatranks_upto # pylint: disable=W0603
    
    m = 0.0000001
    
    if VERY_VERBOSE: print("Hat Event:", HatEventType.toString(event_type))
    
    catch = event_type & (1 << 5)
    add   = event_type & (1 << 4)
    use   = event_type & (1 << 3)
    level = event_type & (0b11)
    
    if catch:
        if level == 1:
            m += 0.01
        elif level == 2:
            m += 0.5
        elif level == 3:
            m += 0.8
        else:
            m += 0.2
    if use:
        if level == 1:
            m += 0.01
        elif level == 2:
            m += 0.6
        elif level == 3:
            m += 0.7
        else:
            m += 0.25
    if add:
        if level == 1:
            m += 0.003
        elif level == 2:
            m += 0.05
        elif level == 3:
            m += 0.1
        else:
            m += 0.05
    hatranks_upto += m
    return m

class HatEventType:
    """Works in a bitwise system: the game.
BushMouth fell off the bottom of the screen. :( whomp whomp. 
HardTail died.
Bits 0-1:
  0: generic
  1: hat level below
  2: hat at current level
  3: hat the level above
Bit 3: catch of hat
Bit 4: add hat
Bit 5: use hat"""
    ADD_HAT = 0b010_00
    ADD_BEL = 0b010_01
    ADD_AT  = 0b010_10
    ADD_ABO = 0b010_11
    CATCH_HAT = 0b001_00
    CATCH_BEL = 0b001_01
    CATCH_AT  = 0b001_10
    CATCH_ABO = 0b001_11
    USE_HAT = 0b100_00
    USE_BEL = 0b100_01
    USE_AT  = 0b100_10
    USE_ABO = 0b100_11
    
    @staticmethod
    def toString(event_type: int) -> str:
        "convert event_type to a human readable string"
        catch = event_type & (1 << 5)
        add   = event_type & (1 << 4)
        use   = event_type & (1 << 3)
        level = event_type & (0b11)
        
        if catch:
            op = 'Caught Hat'
        elif add:
            op = 'Spawned Hat'
        elif use:
            op = 'Use Hat'
        else:
            return 'Null HatEvent'
        
        if level == 1:
            lev = 'Below'
        elif level == 2:
            lev = 'Above'
        else:
            return op
        
        return op + ' ' + lev
    
