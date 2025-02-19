HARDNESS = 1 # medium by default
TITLE = "AAMI crunching"
scr_w = 1024
scr_h = 768
scr_center = (scr_w // 2, scr_h // 2)
FPS = 60

VERSION = 'v1.0.2 BETA'

SHOW_FPS = True
DEBUG = False  # should be False for release versions
VERY_VERBOSE = False # MUST be False in release versions







# make tweaks to settings (programatically, don't change this to change the settings of the game)
DEBUG = DEBUG and __debug__ # debug calls don't happen in optimised mode
VERY_VERBOSE = VERY_VERBOSE and DEBUG # can't be very verbose in not debug mode
tinafey_likelihood = 1024 // HARDNESS # specify likelihood that tina will spawn
