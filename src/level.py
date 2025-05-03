"a class (and, in future, functions) facilitating the whole 'level' thing"

from dataclasses import dataclass

@dataclass
class Level:
    number: int  = -1
    passed: bool = False

class LevelGroup:
    list: list = []
    def __init__(self, *args, repeatLevel=None):
        self.list = list(args)
        if repeatLevel is not None:
            self.repeatlevel = repeatLevel
        else:
            self.repeatlevel = self.list[-1]
    def __getitem__(self, key):
        try:
            return self.list[key]
        except IndexError:
            return self.repeatlevel # repeat last level if out of range