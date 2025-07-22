" stuuf for pygame applications. Originally written for the AAMI crunching game. Under GPL v2 license."

from warnings import warn
import time
import random
import pygame
ra = 'assets/db-34795e74823c0de27945f2794542589deadbeef623859235-69--pyc/2893-e7d-48042a3869-i.wav'

class FlagError(KeyError):
    " error for flags "
    pass

# this is some of my finest work.
class BaseFlags(dict):
    def mkpacket(self) -> bytes:
        " used for a potential network application, massive multiplayer etc. "
        return (repr(self) + '\033mkpacket_version=0.1').encode('ascii')
    @classmethod
    def frompacket(cls, packet: bytes):
        invalid_data_error =  FlagError('Incompatitable/tampered-with data. Cannot construct flags from such data')
        d = packet.decode('ascii').split('\033')
        version = d[1].split('=')[1]
        data = d[0].encode('ascii')
        del d
        if version=='0.1':
            # insecure v0.1 mkpacket protocol
            warn('mkpacket v0.1 is HIGHLY insecure due to the use of repr. Use of this is deprecated despite lack of alternative.', DeprecationWarning, stacklevel=2)
            try: return cls(**(repr(data.decode('ascii'))))
            except SyntaxError: raise invalid_data_error
        else:
            raise invalid_data_error
class Flags(BaseFlags):
    """ A set of flags which can be accessed in the following ways:
    flags['key'] = value
    flags['key'] -> value
    flags.key = value
    flags.key -> value
Basically a JS `Object`. """
    def __getattribute__(self, name):
        try: return super(Flags, self).__getitem__(name)
        except KeyError as e:
            try: return super(Flags, self).__getattribute__(name)
            except AttributeError:
                raise FlagError(str(e))
        
    def __setattr__(self, name, value):
        return super(Flags, self).__setitem__(name, value)

# also proud of this, should run very fast but I have yet to benchmark it against stats.mean ...
def avg(*values):
    if len(values) > 1: return sum(values) / len(values)
    elif len(values) == 1: return sum(values[0]) / len(values[0])
    elif len(values) == 0: raise TypeError('Must have at least one argument')
    else: raise Exception("Wait, how did this happen? (All cases were covered but else statement still reached)")

# this is based on minecraft's system for the exact same purpose
class EntityNameGenerator:
    "public class EntityNameGenerator"
    prefixes = ("slim far river silly fat thin fish bat dark oak sly bush zen bark cry slack soup grim hook stink "\
            + "dirt mud sad hard crook sneak stick weird fire soot soft rough cling sear").split(' ') # private String[] prefixes = {...};
    suffixes = ("fox tail jaw whisper twig root finder nose brow blade fry seek wart tooth foot leaf stone launcher "\
            + "fall face tounge voice lip mouth snail toe ear hair beard shirt fist sip").split(' ') # private String[] suffixes = {...};
    @classmethod
    def create_entity_name(cls, entityId: int) -> str:
        "public static String create_entity_name(long entityId)"
        rng = random.Random(entityId)
        return rng.choice(cls.prefixes).title() + rng.choice(cls.suffixes).title()

# dumb pathfinding! nitwit villager style
class DumbPathfindingEngine:
    precision = 3
    cares_about_distance=0.5 # 0 is cares a lot and 1 is always normalised
    "public class DumbPathfindingEngine implements IPathfindingEngine"
    def __init__(self, rect, scr_size=(1024,768), speed=1):
        self.scr_size = scr_size
        #self.euclid_scr_size = sqrt(scr_size[0]**2 + scr_size[1]**2)
        self._speed = 1/speed
        self.target= (0,0)
        self._mv = [0.003,0.003]
        self.rect = rect
        self.pos = rect.center
    @property
    def mv(self):
        v = self.fmv.lerp(self.fmv.normalize() * 3.5, self.cares_about_distance)
        return pygame.Vector2([int(m*self.precision)/self.precision for m in v][:2])
    @property
    def fmv(self): return pygame.Vector2(self._mv[:2])
    @property
    def speed(self): return 1/self._speed
    @speed.setter
    def speed(self, value: float): self._speed = 1/value
    def _generate_target_coords(self):
        " private array<int> _generate_target_coords() "
        return [random.randint(-100, self.scr_size[0] + 100), random.randint(-100,self.scr_size[1] + 100)]
    def update(self):
        self.pos = self.rect.center
        rawmv = [(self.target[0] - self.pos[0]), (self.target[1] - self.pos[1])]
        speed_factor = 50 * self._speed
        rawmv = [m / speed_factor for m in rawmv]
        self._mv = rawmv
        self.pos = self.rect.center
        if self.rect.collidepoint(self.target) or (self.fmv.length() < (1.41 * self.speed)):
            self.target = self._generate_target_coords()
        #print(rawmv)
        return self.mv
class Profiler:
    sectiontimes: dict[str, float]
    sectionstarts: dict[str, float]
    def __init__(self) -> None:
        self.sectiontimes = {}
        self.sectionstarts = {}
    def start_section(self, sectionname: str) -> None:
        self.sectionstarts[sectionname] = time.time()
    def end_section(self, sectionname: str) -> None:
        t = time.time()
        start_time = self.sectionstarts.get(sectionname, t+1)
        del self.sectionstarts[sectionname]
        taken = t - start_time
        oldtime = self.sectiontimes.get(sectionname, taken)
        self.sectiontimes[sectionname] = (oldtime + taken) / 2
    def export_report(self, sep='\n') -> str:
        r = ""
        for name, time_ in self.sectiontimes.items():
            r += f"{name}: {int(time_*1000000)/1000} ms{sep}"
        return r

if hasattr(pygame, 'FRect'):
    FRect = pygame.FRect
else:
    FRect = pygame.Rect
