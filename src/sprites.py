"sprites for the AAMI crunching game"

from __future__ import annotations

__license__ = 'This is pretty important for the (very much) paid game "Crunch those AAMIs" so i don\'t really think you should be stealing this code.' # just kidding!

import os
import sys
import math
import random
import pygame
from io import StringIO
from pygame.locals import USEREVENT, \
     K_w, K_a, K_s, K_d, K_SPACE, K_c, \
     SRCALPHA
import stuuf
import effect
from settings import *
import util

flags: stuuf.Flags = stuuf.Flags() # should be set to proper flags
next_AAMI_speed = 4.8 + (HARDNESS // 2)
next_entityID = id(flags) # should be pretty random
deathmsgs = StringIO()


def setflags(_flags: stuuf.Flags):
    global flags
    flags = _flags
def load_deathmessage_log(log):
    global deathmsgs
    deathmsgs = log

def noesc(s) -> str:
    r = ''
    inesc = False 
    for c in s:
        if c == '\033':
            inesc = True
        if not inesc: r += c
        if inesc and c == 'm':
            inesc = False 
    return r
def logdeath(*args, **unused):
    if __debug__:
        if VERY_VERBOSE:
            if sys.stdout.isatty():
                print(*args)
            else:
                print(*[noesc(arg) for arg in args])
        print(*[noesc(arg) for arg in args], file=deathmsgs)

class Entity(pygame.sprite.Sprite):
    entityId: int
    entityName: str
    dead: bool = False
    effects: list[effect.Effect]
    canCrunchTina: bool = False
    rect: pygame.Rect
    surf: pygame.Surface
    last_mv: pygame.math.Vector2 = pygame.Vector2(0)
    def __init__(self, *args, **kwargs):
        self.effects = []
        global next_entityID
        self.entityId = next_entityID
        next_entityID += 1
        self.entityName = kwargs.get('entityName', None)
        super(Entity, self).__init__(*args)
        self.rect = stuuf.FRect(scr_center, (10,10))
        logdeath(kwargs.get('joinmsg_format', '') + self.getName(), kwargs.get('joinmsg', 'joined the game.'), '\033[0m')
    def __repr__(self) -> str:
        clsName = self.__class__.__name__
        name = self.getName()
        nGroups = len(self.groups())
        return f"<{clsName} Entity \"{name}\" (in {nGroups} groups)>"
    def update_logic(self):
        if not isinstance(self, Player) and DEBUG:
            print("WARNING: Using inherited update_logic from base Entity class in", repr(self))
        assert self.rect is not None
        for effect_ in self.effects:
            effect_.apply_on_tick()
    @property
    def hasCustomName(self):
        return self.entityName is not None
    def kill(self, reason='died.'):
        logdeath(self.getName(), reason, ":( whomp whomp. ")
        super(Entity, self).kill()
    def getName(self) -> str:
        if self.hasCustomName:
            return self.entityName
        else:
            return stuuf.EntityNameGenerator.create_entity_name(self.entityId)
    def is_on_screen(self) -> bool:
        rect = self.rect
        if rect.bottom < 0:
            return False
        if rect.top > scr_h:
            return False
        if rect.right < 0:
            return False
        if rect.left > scr_w:
            return False
        return True
    def update_pos(self):
        mv = self.mv
        mv += pygame.Vector2(self.last_mv) / 2
        self.rect.move_ip(mv)

class Hat(Entity):
    hatId: str
    def __init__(self, posx=10, hat_id='basic', on=None, posy=0):
        super(Hat, self).__init__()
        self.hatId = hat_id
        self.on   = on # may be player, or technically any other entity...
        self.surf = self._load_hat(hat_id)
        self.mv = [0,0]
        if on is None: rect = self.surf.get_rect(centerx=posx, bottom=posy)
        else: rect = self.surf.get_rect(centerx=on.rect.centerx, bottom=on.rect.top + 8)
        self.rect = stuuf.FRect(rect)
    def _load_hat(self, hat_id):
        if hat_id != 'null':
            return pygame.image.load(os.path.join('assets',
                                                  'hats', hat_id + '.png'))
        else:
            return pygame.Surface([100,100], SRCALPHA)
    def update_logic(self):
        " only call on falling hats "
        self.mv[1] += 1
    def update_pos(self):
        shortmv = pygame.Vector2(1.24, 2.125)
        on = self.on
        if on is not None:
            self.rect = self.surf.get_rect(centerx=on.rect.centerx, bottom=on.rect.top + 8)
            self.mv = [0,0]
        self.rect.move_ip(self.mv)
        
        # make fiery hats catch fire at random
        if random.random() < 0.05 and self.hatId == 'fiery-hat':
            self.surf = self._load_hat('burning-fiery-hat')
        
        # repulsive hats emit particles
        if self.hatId == 'repulsive-hat':
            # emit particle
            angle = random.random() * 360
            particle = Particle('repulsion',
                                self.rect.center,
                                shortmv.rotate(angle),
                                rotspeed=random.random() * 1.5 + 0.5,
                                start_angle=random.random()*45 + angle)
            flags.vfx.add(particle)
    def activate_special_ability(self) -> int:
        "activate the special ability of this hat. Returns hatevent."
        global flags
        if self.hatId == 'wizardry': # the proper mode
        #if True and DEBUG: # just for testing, it won't do this in production mode (__debug__ == False)
            mypos = pygame.Vector2(self.on.rect.center)
            AAMIs: pygame.sprite.Group = flags.AAMIs
            tinas: pygame.sprite.Group = flags.tinas
            tinatainer = flags.tinatainer # tinacontainer
            closest_aami: AAMI = None
            closest_aami_dist: float = 42e1000000000000000000000000000000000000000000000 # basically +inf
            closest_tina: TinaFey = None
            closest_tina_dist: float = 42e1000000000000000000000000000000000000000000000 # basically +inf
            
            # attack main tina if present
            if tinatainer.has_tina():
                flags.vfx.add(LightningBolt(tinatainer.get_tina().rect, attack_center=True))
                tinatainer.set_null_tina()
                return effect.HatEventType.USE_ABO # attacking a tina with a wizardry hat is always the highest possible use for a hat
            
            for aami in AAMIs:
                aamipos = pygame.Vector2(aami.rect.center)
                dist = (aamipos - mypos).length()
                if dist < closest_aami_dist:
                    closest_aami = aami
            for tina in tinas:
                tinapos = pygame.Vector2(tina.rect.center)
                dist = (tinapos - mypos).length()
                if dist < closest_tina_dist:
                    closest_tina = tina
            try: aamipos = pygame.Vector2(closest_aami.rect.center)
            except AttributeError: return 0 # if there is no AAMI to attack, don't bother
            try:
                tinapos = pygame.Vector2(closest_tina.rect.center)
                aamidist= (mypos - aamipos).length()
                tinadist= (mypos - tinapos).length() * 0.98 # slight pereference to attack tinas (tinas have their distance slightly shortened)
                if aamidist < tinadist:
                    to_kill = closest_aami
                else:
                    to_kill = closest_tina
            except AttributeError:
                to_kill = closest_aami
            if VERY_VERBOSE: print("Attacking", repr(to_kill), "in a cool-looking way")
            if to_kill is closest_aami:
                flags.score += 1
                to_kill.crunched = True
                to_kill.crunchedBy = 'The Ancient Magic' # oooooooooooh, implies lore!!!
                flags.vfx.add(LightningBolt(to_kill.rect))
            else:
                # attack `to_kill` in a cool-looking way
                flags.vfx.add(LightningBolt(to_kill.rect))
                to_kill.kill()
            
            rank = effect.hatByRank.index(self.hatId)
            currentrank = math.floor(effect.get_hatranksupto())
            
            if rank > currentrank:
                return effect.HatEventType.USE_ABO
            else:
                return effect.HatEventType.USE_HAT
            # wizardry hat is never below
        return 0 # null hatevent


class Player(Entity):
    currenthat: Hat = None
    crunchedBy: str = None
    speed: int = 5
    def __init__(self, pos=scr_center, hat=None):
        # variable representing the state of the player and stuff
        self.direction = 0 # `0` is right (->)
        self.mv = (0,0) # movement vector
        self.crunching = False
        self.img_in_use= 'standing'
        self.crunched  = False # can only be crunched by Tina Fey
        self.currenthat= hat
        if hat is not None:
            self.currenthat.on = self
        # inherit from Entity stuff (i don't get it)
        super(Player, self).__init__(entityName='Noswald')
        # surfaces and images
        self.standing = pygame.transform.flip(pygame.image.load(os.path.join('assets',
                                                                             'dude_standing.png')), True, False) # do convert_alhpa on blit
        self.walking1 = pygame.image.load(os.path.join('assets', 'dude_walking-1.png'))
        self.walking2 = pygame.image.load(os.path.join('assets', 'dude_walking-2.png'))
        self.surf = pygame.surface.Surface((100,100), SRCALPHA)
        self.rect = stuuf.FRect(self.surf.get_rect(center=pos))
        self.surf.blit(self.standing.convert_alpha(), (0,0))
    def update_pos(self):
        self.rect.move_ip(self.mv)
        # keep player on screen
        rect = self.rect
        if rect.left < 0:
            self.rect.left = 0
        if rect.right > scr_w:
            self.rect.right = scr_w
        if rect.top <= 0:
            self.rect.top = 0
        if rect.bottom >= scr_h:
            self.rect.bottom = scr_h
        
        # handle being crunched, probably should be in `update_logic`
        if self.crunched and not self.dead:
            logdeath("\033[1mNoswald", "was crunched", (f"by {self.crunchedBy}.\033[0m" if self.crunchedBy is not None else '.'))
            if not VERY_VERBOSE: print("\033[1mNoswald", "was crunched", (f"by {self.crunchedBy}.\033[0m" if self.crunchedBy is not None else '.'), flush=True)
            self.dead = True
    def update_keypresses(self, pressed_keys):
        if VERY_VERBOSE and random.random() < 0.05: print("updating player position")
        
        speed = self.speed
        
        if pressed_keys[K_SPACE]:
            # jump
            self.jumping = True
            self.jump = 0 # goes up to 180
            self.preJumpHeight = self.rect.centery
        walking = False
        if pressed_keys[K_c]:
            self.crunching = True
        else:
            self.crunching = False
        if pressed_keys[K_w]:
            self.direction = 1
            self.rect.move_ip(0, -speed)
            walking = True
        if pressed_keys[K_s]:
            self.direction = 1
            self.rect.move_ip(0, speed)
            walking = True
        if pressed_keys[K_a]:
            self.direction = 1
            self.rect.move_ip(-speed, 0)
            walking = True
        if pressed_keys[K_d]:
            self.direction = 0
            self.rect.move_ip(speed, 0)
            walking = True
        if walking:
            self.surf.fill((0,0,0,0))
            self.img_in_use = 'walking1'
            self.surf.blit(pygame.transform.flip(self.walking1, bool(self.direction), False), (0,0))
        else:
            self.surf.fill((0,0,0,0))
            self.img_in_use = 'standing'
            self.surf.blit(self.standing, (0,0))
    def renderhat(self, surf):
        if self.current_hat is not None:
            surf.blit(self.current_hat.surf, self.current_hat.rect)
    def update_logic(self, particles):
        ### TEST PARTICLES ###
        # which work now!!!
        super().update_logic()
        """if DEBUG:
            flags.vfx.add(Particle('bread', self.rect.center))"""
class AAMI(Entity): # implements ICrunchable
    crunchedBy: str = None
    def __init__(self, pos=(0, scr_center[1])):
        global next_AAMI_speed
        self.mv = pygame.Vector2((random.gauss(next_AAMI_speed, 1)),(random.gauss(0,0.256)))
        #if not flags.you_won: next_AAMI_speed += 0.1
        #else: next_AAMI_speed -= 0.003
        self.crunched = False # are we crunched yet?
        super(AAMI, self).__init__()
        self.surf = pygame.surface.Surface((160,80))
        self.img = pygame.image.load(os.path.join('assets', 'AAMI.png')).convert()
        self.rect = stuuf.FRect(self.surf.get_rect(bottomright=pos))
        self.surf.blit(pygame.transform.scale(self.img, (160,80)), (0,0))
    def update_logic(self):
        rect = self.rect
        if (rect.right <= 0) or (rect.left > scr_w) or \
           (rect.top > scr_h) or (rect.bottom <= 0):
            self.kill("fell off the screen.")
        if self.crunched:
            self.kill("was crunched" + (f' by {self.crunchedBy}' if self.crunchedBy is not None else '') + ".")
class DoorDacker(Entity): # implements ISmackable
    bike = pygame.image.load(os.path.join('assets', 'doordack_bike-only.png'))
    img  = pygame.image.load(os.path.join('assets', 'doordack_bike.png'))
    hand = pygame.image.load(os.path.join('assets', 'doordack_hand-only.png')) # the hand from the 'smash it' ads
    def __init__(self, pos=(0,0)):
        super().__init__()
        self.surf = random.choice([self.bike, self.bike, self.img])
        self.rect = self.surf.get_rect(bottomright=pos)
        self.mv = pygame.Vector2((random.gauss(5, 1), random.gauss(0,0.256)))
    def update_logic(self):
        rect = self.rect
        if (rect.right <= 0) or (rect.left > scr_w) or \
           (rect.top > scr_h) or (rect.bottom <= 0):
            self.kill("fell off the screen.")
class TinaFey(Entity):
    speed = ((1 + HARDNESS) / 2) / 500
    container: util.TinaContainer
    def __init__(self, pos=(200,200), target: Entity = None, logic=True, do_dumb_pathfinding=False, container=None):
        super(TinaFey, self).__init__(entityName='Tina Fey')
        self.target = target
        self.img  = pygame.image.load(os.path.join('assets', 'TinaFey.png')).convert_alpha()
        self.surf = pygame.transform.scale(self.img, (240,240))
        self.rect = stuuf.FRect(self.surf.get_rect(center=pos))
        self.mv   = pygame.Vector2(int(random.uniform(0,2)), int(random.uniform(0,2)))
        self.last_mv = self.mv
        self.container = container # util.TinaContainer
        if container is not None:
            self.container.set_tina(self)
        if HARDNESS < 5:
            if self.rect.colliderect(flags.player.rect):
                if VERY_VERBOSE: print("Tina was in hitbox")
                self.kill('tried to spawn in the player\'s hitbox, which, frankly, is unfair.')
        else:
            print("<TinaFey> Deal with it.")
        #self.dumbpathfinding= do_dumb_pathfinding # old and deprecated
        self.dumbpathfinding = None
        if do_dumb_pathfinding:
            self.dumbpathfinding = stuuf.DumbPathfindingEngine(self.rect, (scr_w, scr_h))
        if logic: self.update_logic()
    def kill(self, reason: str=''):
        super().kill(reason)
        if self.container is not None:
            if VERY_VERBOSE: print("Container is not None")
            self.container.set_null_tina()
    def update_logic(self):
        if self.dumbpathfinding is None:
            mvx=0
            mvy=0
            selfrect = self.rect
            selfx = selfrect.centerx
            selfy = selfrect.centery
            speed = 1 / self.speed
            omvx = int((random.uniform(0, scr_w) - selfx) / (-1 + speed)) # go towards random
            omvy = int((random.uniform(0, scr_h) - selfy) / (-1 + speed)) # location, chosen
            #                                                             # every tick
            if self.target is not None:
                targetrect = self.target.rect
                targetx = targetrect.centerx
                targety = targetrect.centery
                mvx = (targetx - selfx) / speed
                mvy = (targety - selfy) / speed
                self.mv = [stuuf.avg(mvx, mvx, omvx), stuuf.avg(mvy, mvx, omvx)]
            else: self.mv = [omvx, omvy]
        else: # do dumb pathfinding
            self.dumbpathfinding.update()
            #if VERY_VERBOSE: print(self.dumbpathfinding.mv) # too much
            self.mv = self.dumbpathfinding.mv
        self.mv = pygame.Vector2(self.mv)
        self.last_mv = self.mv
    
class SnoopDogg(Entity):
    img = pygame.image.load(os.path.join('assets', 'snoop.png'))
    mv: pygame.math.Vector2 = pygame.Vector2(0.1)
    def __init__(self, pos=(300,300)):
        super().__init__(entityName='Snoop Dogg', joinmsg=' is in da house!', joinmsg_format='\033[1m')
        self.surf = pygame.transform.scale(self.img, (240,240))
        self.rect = stuuf.FRect(self.surf.get_rect(center=pos))
        self.dumbpathfinding = stuuf.DumbPathfindingEngine(self.rect, (scr_w, scr_h), 0.1)
        self.dumbpathfinding.cares_about_distance = 0.8
    def update_logic(self):
        self.last_mv = self.mv / 3
        self.mv = self.mv.lerp(self.dumbpathfinding.update(), 0.6)
        

class VisualEffect(pygame.sprite.Sprite):
    def __repr__(self) -> str:
        clsName = self.__class__.__name__
        groups  = len(self.groups())
        return f'<{clsName} VisualEffect (in {groups} groups)>'
    def is_on_screen(self) -> bool:
        rect = self.rect
        if rect.bottom < 0:
            return False
        if rect.top > scr_h:
            return False
        if rect.right < 0:
            return False
        if rect.left > scr_w:
            return False
        return True
    def kill(self, reason: str=''):
        super().kill()
    def update_logic(self):
        pass
    def update_pos(self):
        pass
    def render(self, surf, show_hitboxes: bool=False):
        pass
class LightningBolt(VisualEffect):
    lifeTimer: int = 0
    life_expectancy: int = 5
    def __init__(self, target: pygame.Rect, *, attack_center: bool=False):
        super().__init__()
        self.surf = pygame.Surface([172, 768], pygame.SRCALPHA)
        if attack_center:
            self.rect = self.surf.get_rect(center=target.center)
        else:
            self.rect = self.surf.get_rect(centerx=target.centerx, bottom=target.top)
        self.targetRect = target
        self.textures = [pygame.transform.scale(
                            pygame.image.load(os.path.join('assets',i)).convert_alpha(),
                            [172, 384]) \
                         for i in ('lightning-1.png', 'lightning-2.png')]
        self.texture_top = pygame.transform.scale(
                pygame.image.load(os.path.join('assets', 'lightning-top.png')),
                [172, 384])
        self.update_gfx()
    def update_gfx(self):
        self.surf.fill((0,0,0,0))
        self.surf.blit(random.choice(self.textures + [self.texture_top]), (0,0))
        self.surf.blit(random.choice(self.textures), (0, 384))
    def update_pos(self):
        self.update_gfx()
        self.rect.centerx = self.targetRect.centerx
        self.rect.bottom = self.targetRect.top
    def update_logic(self):
        self.lifeTimer += 1
        if self.lifeTimer > self.life_expectancy: self.kill()
    def render(self, surf, show_hitboxes: bool=False):
        colour = (240, 200, 255)
        surf.blit(self.surf, self.rect)
        if show_hitboxes:
            pygame.draw.circle(surf, colour, [self.targetRect.centerx, self.targetRect.top], 4)
            pygame.draw.rect(surf, colour, self.rect, 1)

class Particle(VisualEffect):
    mv: pygame.Vector2
    pos:pygame.Vector2
    rng: random.Random
    rotation: float=00
    def __init__(self, texId, start_pos=(0,0), inital_mv=(0,0), seed=None, rotspeed=0, start_angle=0, size=(24,24)):
        super().__init__()
        self.rotspeed = rotspeed
        if seed is None: self.rng = random.Random(hash(random.random()))
        else: self.rng = random.Random(seed)
        self.img = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'particles', texId+'.png')), size)
        self.rect= pygame.FRect(start_pos, size)
        self.pos = pygame.Vector2(start_pos)
        self.rotation = start_angle
        self.mv  = pygame.Vector2(inital_mv)
        self.update_pos()
    def update_pos(self):
        self.rect.move_ip(self.mv)
        self.pos = pygame.Vector2(self.rect.center)
        self.surf = pygame.transform.rotate(self.img, self.rotation)
        self.rect = stuuf.FRect(self.surf.get_rect(topleft=self.rect.topleft))
    def update_logic(self):
        self.rotation += self.rotspeed
        self.mv.y += 1.0101
        #self.mv.rotate_ip(self.rotation/10) # this completely breaks it idk why it was ever here...
    def render(self, surf, show_hitboxes: bool=None):
        srf = pygame.transform.rotate(self.surf, self.rotation)
        if VERY_VERBOSE: print("Particle pos", self.pos)
        rect= srf.get_rect(centerx=self.pos.x, centery=self.pos.y)
        surf.blit(srf, rect)
