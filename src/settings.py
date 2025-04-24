HARDNESS = 1 # medium by default
TITLE = "AAMI crunching"
scr_w = 1024
scr_h = 768
scr_center = (scr_w // 2, scr_h // 2)
FPS = 60
GFX_MODE = 4 # determines how graphics-intensive this should be

VERSION = 'v1.2.0-ALPHA'

SHOW_FPS = True
DEBUG = True  # should be False for release versions
VERY_VERBOSE = False # MUST be False in release versions
RENDER_DEBUG_WINDOW = True







# make tweaks to settings (programatically, don't change this to change the settings of the game)
DEBUG = DEBUG and __debug__ # debug calls don't happen in optimised mode
VERY_VERBOSE = VERY_VERBOSE and DEBUG # can't be very verbose in not debug mode
RENDER_DEBUG_WINDOW = RENDER_DEBUG_WINDOW and DEBUG # only render debug window in debug mode
SHOW_FPS = SHOW_FPS and __debug__
tinafey_likelihood = 1024 // HARDNESS # specify likelihood that tina will spawn
