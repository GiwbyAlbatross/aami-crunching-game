from __future__ import annotations

import random
import math

import pygame

import stuuf
import sprites
import util

from settings import VERY_VERBOSE

class Effect:
    " base class for status effects "
    associated_hat_id: str = 'null'
    name: str
    bubble_colour: pygame.Color = pygame.Color(0,0,0)
    
    currently_on: sprites.Entity
    level: int
    def __init__(self, entity: sprites.Entity, level: int=1, **unused):
        self.currently_on = entity
        self.level = level
    def apply_once(self):
        pass
    def apply_on_tick(self):
        #self.apply_once() # [DONE] come up with better way to do that
        pass
class Speed(Effect):
    " makes you run faster! (not snake oil) "
    name: str = 'speed'
    associated_hat_id: str = 'fiery-hat' # to be inplemented
    
    def apply_once(self):
        self.currently_on.speed = random.gauss(5 + self.level, 0.5)
class Repulsiveness(Effect):
    " repells tinas "
    name: str = 'repulsiveness'
    tina: sprites.TinaFey
    tinas: pygame.sprite.Group
    def __init__(self, entity: sprites.Entity, level: int, tina: util.TinaContainer, tinas: pygame.sprite.Group=..., **unused):
        super(Repulsiveness, self).__init__(entity, level)
        self.tina = tina
        self.tinas = tinas
    def _apply_to_tina(self, tina: sprites.TinaFey):
        try:
            user = self.currently_on
            try: away_mv = pygame.Vector2(tina.rect.centerx - user.rect.centerx, tina.rect.centerx - user.rect.centerx).normalize()
            except ValueError: away_mv = pygame.Vector2()
            away_mv *= self.level * 3
            tina.rect.move_ip(away_mv)
        except AttributeError: pass
    def apply_on_tick(self):
        tina = self.tina.get_tina()
        self._apply_to_tina(tina)
        for other_tina in self.tinas:
            self._apply_to_tina(other_tina)

effects: dict = {'repulsiveness':Repulsiveness, 'speed':Speed}
effectByHat: dict = {'fiery-hat':Speed, 'repulsive-hat':Repulsiveness}

hatByRank: list = ['basic', 'top', 'spotty', 'repulsive-hat', 'fiery-hat', 'wizardry'] # so -1 is wizardy as well
hatranks_upto = 0.003 # starting value

def rand_lower() -> float:
    a = random.random()
    return (abs(2/(a-2)) - 0.5) * 2

def add_effect_from_hat(entity: sprites.Entity, hat: sprites.Hat, **kwargs) -> Effect:
    args = kwargs.copy()
    args['level'] = int((hatranks_upto % 1) * 5)
    args['entity']= entity

    try:
        effect_constructor = effectByHat[hat.hatId]
        
        effect = effect_constructor(**args)# should perhaps be called kwargs, kwds or kws but whatever
        
        try: entity.effects = entity.effects[1:]
        except IndexError: pass
        entity.effects.append(effect)
    except KeyError:
        return Effect(entity)
    else:
        return effect

def get_hat(**kwargs) -> tuple[sprites.Hat, int]:
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
    return hatranks_upto

def process_aquire_hat(hat: sprites.Hat) -> int:
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
    global hatranks_upto
    
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
    """Works in a bitwise system:
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
    
