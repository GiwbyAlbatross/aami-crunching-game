HARDNESS = 1 # medium by default
TITLE = "AAMI crunching" # window title
scr_w = 1024 # # window
scr_h = 768 #  # size
FPS = 60 # target FPS
GFX_MODE = 4 # determines how graphics-intensive this should be

VERSION = 'v1.2.3-ALPA'

SHOW_FPS = True
DEBUG = True  # should be False for release versions
VERY_VERBOSE = True # MUST be False in release versions
RENDER_DEBUG_WINDOW = False

#
#
#
#
#

# make tweaks to settings (programatically, don't change this to change the settings of the game)
DEBUG = DEBUG and __debug__ # debug calls don't happen in optimised mode
VERY_VERBOSE = VERY_VERBOSE and DEBUG # can't be very verbose in not debug mode
RENDER_DEBUG_WINDOW = RENDER_DEBUG_WINDOW and DEBUG # only render debug window in debug mode
SHOW_FPS = SHOW_FPS and __debug__ # don't show FPS counter in optimised mode
tinafey_likelihood = 1024 // HARDNESS # specify likelihood that tina will spawn
GFX_MODE = GFX_MODE if __debug__ else max(GFX_MODE, 3) # don't push graphics too high in optimised mode
scr_center = (scr_w // 2, scr_h // 2)
scr_size = (scr_w, scr_h)
