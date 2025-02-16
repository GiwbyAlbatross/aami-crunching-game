" generic run script written for the AAMI crunching game "

from sys import exit, executable, platform
from os import system
system('clear' if platform != 'win32' else 'cls')
exit(system('{} src/main.py'.format(executable)))