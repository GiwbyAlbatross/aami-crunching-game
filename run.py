" generic run script written for the AAMI crunching game "

from sys import exit, executable, platform # pylint: disable=W0622
from os import system
system('clear' if platform != 'win32' else 'cls')
exit(system(f'{executable} src/main.py'))
