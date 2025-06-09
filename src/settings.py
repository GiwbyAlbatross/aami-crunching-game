import argparse

HARDNESS = 1 # medium by default
TITLE = "AAMI crunching" # window title
scr_w = 1024 # # window
scr_h = 768 #  # size
FPS = 60 # target FPS
GFX_MODE = 4 # determines how graphics-intensive this should be
FULLSCREEN = False
DRAW_ON_SCREENSHOT = False 

VERSION = 'v1.2.4-ALPHA'

SHOW_FPS = True
DEBUG = True  # should be False for release versions
VERY_VERBOSE = False # MUST be False in release versions
RENDER_DEBUG_WINDOW = True

#   Here's a fun ASCII-art beacon for you to look at
# #
# # # ---------------------------------------------------------------------------------------------
# #
#

# process command-line arguments
parser = argparse.ArgumentParser(prog='aami-crunching-game', exit_on_error=False)
parser.add_argument('-F', '--fullscreen', action='store_true', help="Run The AAMI Crunching Game in fullscreen mode. Runs at 1080p by default.")
parser.add_argument('-V', '--debug', action='store_true', help='Show additional debug information when running the game.')
parser.add_argument('-d', '--difficulty', type=int, help="Difficulty for the game. Controlls a few things. A positive integer.", default=HARDNESS)
parser.add_argument('-G', '--gfx-level', '--graphics-level', type=int, help="How graphics-intensive to make the game. A positive integer.", default=GFX_MODE)
parser.add_argument('--transparent', action='store_true', help="Pretend the AAMI crunching game is on a transparent window. Requires scrot.")
args = parser.parse_args()
FULLSCREEN = args.fullscreen
DEBUG = DEBUG or args.debug
GFX_MODE = args.gfx_level
HARDNESS = args.difficulty
DRAW_ON_SCREENSHOT = args.transparent

# make tweaks to settings (programatically, don't change this to change the settings of the game)
DEBUG = DEBUG and __debug__ # debug calls don't happen in optimised mode
VERY_VERBOSE = VERY_VERBOSE and DEBUG # can't be very verbose in not debug mode
RENDER_DEBUG_WINDOW = RENDER_DEBUG_WINDOW and DEBUG # only render debug window in debug mode
SHOW_FPS = SHOW_FPS and __debug__ # don't show FPS counter in optimised mode
tinafey_likelihood = 1024 // HARDNESS # specify likelihood that tina will spawn
GFX_MODE = GFX_MODE if __debug__ else max(GFX_MODE, 3) # don't push graphics too high in optimised mode
FULLSCREEN = FULLSCREEN or DRAW_ON_SCREENSHOT
scr_center = (scr_w // 2, scr_h // 2)
scr_size = (scr_w, scr_h)


# process fullscreen
if FULLSCREEN:
    """ # get display aspect ratio and conform to it, with different resolution (broken-ish)
    import pygame
    pygame.init()
    dpyinfo = pygame.display.Info()
    aspect_ratio = dpyinfo.curent_w / dpyinfo.current_h
    #aspect_ratio = 16/9
    scr_w = int(scr_h * aspect_ratio)
    if DEBUG: print(f'\033[1mscr_w: {scr_w}, scr_h: {scr_h}\033[0m')
    if __name__ == '__main__': pygame.quit()"""
    # assume fullscreen means 16:9 monitor (fix this later, the above code should work but doesn't)
    scr_w, scr_h = 1920, 1080

# process screen size
scr_center = (scr_w // 2, scr_h // 2)
scr_size = (scr_w, scr_h)

if __name__ == '__main__':
    k,v = ..., ...
    for k, v in globals().items():
        if k == v: continue
        print(f'{k} = {v!r}')