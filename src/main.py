" The AAMI crunching game. "

__lisence__ = 'Um the AAMI crunching game is a paid game (totally). ' # of course, this is a joke, but I once had intenions to sell the game

"""
TODO:
- implement second level [ALMOST DONE]
- add status effects from hats [DONE]
- REMOVE * IMPORTS TO MAKE LINTER HAPPY [DONE
"""

# pylint: disable=C0413
# pylint: disable=C0103
import os
import math
import random
import pygame
from pygame.locals import QUIT, KEYDOWN, USEREVENT, \
     K_ESCAPE, K_F3, K_z, K_SPACE, \
     FULLSCREEN, SRCALPHA
import stuuf
from settings import ( # so that all of the modules share the same constants...
                      HARDNESS,
                      FPS,
                      TITLE,
                      scr_w, scr_h,
                      scr_center,
                      scr_size,
                      tinafey_likelihood,
                      SHOW_FPS,
                      DEBUG,
                      VERY_VERBOSE,
                      VERSION,
                      RENDER_DEBUG_WINDOW,
                      GFX_MODE,
                      FULLSCREEN,
                      DRAW_ON_SCREENSHOT
)
from sprites import (
                     setflags,
                     load_deathmessage_log,
                     Entity,
                     Hat,
                     Player,
                     AAMI,
                     DoorDacker,
                     TinaFey,
                     SnoopDogg,
                     Particle,
                     VisualEffect,
                     LightningBolt,
)
import effect
import menus
import util
from level import Level, LevelGroup

print(f"AAMI Crunching Game. version: {VERSION}")

current_fps = FPS # update sometimes I guess
target_fps  = FPS # lower in menu to save CPU cycles
scorestr = "Score: %02d"
fps_frmt = "FPS: %03f"
#if DEBUG: tinafey_likelihood = 128 # makes tina VERY likely to spawn, for testing features involving tina
TEST_EFFECTS = False # this is for specific debug purposes only

# dev stuff
if not DEBUG:
    import warnings
    warnings.filterwarnings('ignore', category=RuntimeWarning)
    warnings.filterwarnings('ignore', category=DeprecationWarning)

def renderscore(surf):
    return surf.blit(pygame.font.Font(None, 128).render(scorestr % flags.score,
                                                 False, (240,240,242)), (10,10))
def renderFPS(surf, fps):
    return surf.blit(pygame.font.Font(None, 24).render(fps_frmt % fps, False,
                                                (242,240,240)), (12, scr_h - 32))

if __name__ == '__main__':
    pygame.init()

    if DRAW_ON_SCREENSHOT:
        try: os.remove('/tmp/aami-crunching-backdrop.png')
        except FileNotFoundError: pass
        os.system('scrot /tmp/aami-crunching-backdrop.png')

    # open a window
    scr = pygame.display.set_mode((scr_w, scr_h), pygame.FULLSCREEN if FULLSCREEN else 0)
    # set the window title
    pygame.display.set_caption('Loading... | %s' % TITLE)
    # and loading screen
    try:
        scr.blit(pygame.image.load(os.path.join('assets', 'loading.png')), (0,0))
        pygame.display.update()
    except FileNotFoundError as e:
        pygame.quit()
        print("ERROR: loading image not found. perhaps run from wrong directory.")
        print(f"Real Exception: {type(e).__name__}: {str(e)}")
        raise SystemExit(1)
    if DRAW_ON_SCREENSHOT:
        # fun backdrop :)
        backdrop = pygame.transform.scale(
            pygame.image.load('/tmp/aami-crunching-backdrop.png'),
            scr_size)
        scr.blit(backdrop, (0,0))
    paused_scr = scr.copy()
    # and icon
    try: pygame.display.set_icon(pygame.image.load(os.path.join('assets', 'dude_standing.png')))
    except pygame.error: pass # ignore any errors, this isn't essential
    # state variables
    running = 1
    AAMIs_crunched = 0
    you_won_fname = ...
    winning_music = ...
    flags = stuuf.Flags(running=True, you_won=False, show_hitboxes=False, level=0, paused=False) # level = 0 for release
    flags.running = running
    flags.score = AAMIs_crunched
    flags.levels = LevelGroup(Level(number=0, passed=True), Level(number=1, passed=False))
    setflags(flags) # from sprites.py
    
    if DEBUG: # debug window and stuff
        flags.debugwindow = menus.DebugWindow(flags)
    flags.mainmenu = menus.MainMenu()

    # open logs
    deathmsgs = open('death-messages.log', 'wt')
    load_deathmessage_log(deathmsgs) # also from sprites.py
    
    # events
    GAME_TICK = USEREVENT + 1
    pygame.time.set_timer(GAME_TICK, (1024 // 20)) # 20 times a 'second' (second is 1024 millis)
    ADD_AAMI = USEREVENT + 2
    pygame.time.set_timer(ADD_AAMI, (512 * ((HARDNESS + 1)//2)))
    GET_FPS = USEREVENT + 3
    pygame.time.set_timer(GET_FPS, 768)
    RESET = USEREVENT + 4
    #pygame.mixer.set_endevent(RESET)

    # load and initializse sounds
    pygame.mixer.init()
    crunch = pygame.mixer.Sound(file=os.path.join('assets',
                                                  'soundfx',
                                                  'crunch.wav'))
    so_many_tinafeys = pygame.mixer.Sound(file=os.path.join('assets',
                                                  'soundfx',
                                                  'so_many_tinafeys.wav'))
    bodydoubles_short = pygame.mixer.Sound(file=os.path.join('assets',
                                                  'soundfx',
                                                  'so_i_hired_body_doubles.wav'))
    bodydoubles_long  = pygame.mixer.Sound(file=os.path.join('assets',
                                                  'soundfx',
                                                  'so_i_hired_body_doubles_to_help.wav'))


    # sprites and groups for said sprites
    player = Player()
    flags.player = player
    currenthat: Hat = Hat('null', on=player)
    player.currenthat = currenthat
    tina = None
    tinacontainer = util.TinaContainer()
    doordack_orders: list = []
    flags.tinatainer = tinacontainer
    flags.doordack_orders = doordack_orders
    AAMIs = pygame.sprite.Group()
    doordackers = pygame.sprite.Group()
    tinas = pygame.sprite.Group()
    snoopDoggs = pygame.sprite.Group()
    falling_hats = pygame.sprite.Group()
    visualEffects = pygame.sprite.Group()
    flags.AAMIs = AAMIs
    flags.tinas = tinas
    flags.vfx = visualEffects # which includes particles now
    flags.doordackers = doordackers
    flags.snoops = snoopDoggs

    profiler = stuuf.Profiler()
    flags.profiler = profiler
    
    # test effects
    if DEBUG and TEST_EFFECTS:
         e = effect.BaseAAMIAtrractor(player, level=1, aamis=AAMIs)
         e.apply_once()
         player.effects.append(e)
    
    # you won screen
    you_won  = ...
    you_died = pygame.image.load(os.path.join('assets', 'you_died.png')).convert_alpha()
    flags.mainmenu.build_contents()

    # clock
    tiktok = pygame.time.Clock()
    dt = 20

    pygame.display.set_caption(TITLE)

    while running:
        profiler.start_section('total')
        tina = tinacontainer.get_tina()
        try:
            profiler.start_section('event_processing')
            for event in pygame.event.get():
                if flags.paused and event.type in menus.MENU_EVENTS: flags.mainmenu.process_event(event)
                if event.type == QUIT:
                    running = 0
                    flags.running = False
                elif event.type == GAME_TICK:
                    current_fps = tiktok.get_fps() # get current FPS every once in a while
                    if DEBUG: flags.debugwindow.update() # update this every tick regardless of game paused-ness
                    if flags.paused: continue # skip ticks when paused
                    profiler.start_section('tick')
                    # do game tick stuff
                    player.update_logic() # this being commented out caused issue #5
                    player.currenthat = currenthat
                    AAMIs_crunched = flags.score
                    before_AAMIs_crunched = AAMIs_crunched
                    for hat in falling_hats:
                        hat.update_logic()
                    for aami in AAMIs:
                        aami.update_logic()
                        if aami.rect.colliderect(player.rect) and player.crunching \
                           and (not aami.crunched):
                            aami.crunched = True
                            aami.crunchedBy = 'Noswald'
                            AAMIs_crunched += 1
                            crunch.play()
                        if tinacontainer.has_tina():
                            if tina.rect.contains(aami.rect) and (random.random() > 0.25):
                                aami.crunched = True
                                aami.crunchedBy = 'Tina Fey'
                                if random.random() > 0.1:
                                    crunch.play()
                            # tina can now crunch AAMIs
                    for harmless_tina in tinas:
                        harmless_tina.update_logic()
                        if not harmless_tina.is_on_screen():
                            harmless_tina.kill('fell off the screen.')
                    tobe_fallinghats = []
                    for hat in falling_hats:
                        hat.update_logic()
                        if player.rect.colliderect(hat.rect):
                            """
                            if currenthat is not None:
                                currenthat.kill()
                                currenthat.add(falling_hats)
                                currenthat.on = None
                            """
                            if currenthat is not None:
                                currenthat = hat
                                currenthat.on = player
                            player.current_hat = hat
                            hat.kill()
                            hatevent = effect.process_aquire_hat(hat)
                            effect.add_effect_from_hat(player,
                                                       hat,
                                                       tina=tinacontainer,
                                                       tinas=tinas,
                                                       aamis=AAMIs).apply_once()
                            effect.process_hat_event(hatevent)
                            if DEBUG: flags.debugwindow.log_hatevent(hatevent)
                            fakeFallingHat = Hat(posx=hat.rect.centerx, posy=hat.rect.centery, hat_id=hat.hatId)
                            tobe_fallinghats.append(fakeFallingHat)
                        if hat.rect.top > scr_h:
                            hat.kill('fell off the bottom of the screen.') # kill hats that fell off the screen
                    for hat in tobe_fallinghats: hat.add(falling_hats)
                    del tobe_fallinghats
                    if tinacontainer.has_tina():
                        if tina.rect.colliderect(player.rect):
                            player.crunched = True
                            player.crunchedBy = 'Tina Fey, with love'
                            crunch.play()
                            pygame.display.set_caption("You lost | %s" % TITLE)
                        tina.update_logic()
                        if not tina.is_on_screen():
                            tina.kill('fell off the screen.')
                            tinacontainer.set_null_tina()
                            tina = None # she'll respawn, don't worry
                    else: pass # there is no tina fey (only Zuhl)
                    
                    if before_AAMIs_crunched != AAMIs_crunched:
                        print(f"AAMIs crunched: {AAMIs_crunched}                           ")
                        # load assets for winning  :)
                        if AAMIs_crunched > 40 and you_won_fname is ...: # leave ellipsis in
                            you_won_fname = os.path.join('assets', 'you_won.png')
                            if VERY_VERBOSE: print("Generated you_won_fname")
                        if AAMIs_crunched > 45 and you_won is ...: #     # leave ellipsis in
                            you_won = pygame.image.load(you_won_fname)
                            if VERY_VERBOSE: print("Loaded you_won")
                        if AAMIs_crunched > 48 and winning_music is ...: # ...
                            if VERY_VERBOSE: print("Loading music for when you win :)")
                            winning_music = not None
                            pygame.mixer.music.load(stuuf.ra)
                        if AAMIs_crunched >= 50:
                            # you won
                            if not flags.you_won:
                                print("You Won!")
                                flags.you_won = True
                            pygame.display.set_caption("You Won! | AAMI crunching")
                            pygame.mixer.music.play(0)
                        # interestingly, just spamming Z with the wizardry hat can get more than 50 AAMIs
                        # but you have to do some actual work (manually crunch an AAMI) in order to get the
                        # 'You Won' screen and level up. BUG: spamming Z slowly increases XP, even without hat
                        del before_AAMIs_crunched
                        flags.score = AAMIs_crunched
                    
                    # spawn tina
                    if random.randint(0,tinafey_likelihood) == 1: # rare, but can happen
                        if not tinacontainer.has_tina():
                            # SPAWN A TINA FEY!!!!!!!!!!
                            tina = TinaFey(pos=[random.randint(0, scr_w), random.randint(0,scr_h)],
                            #tina = TinaFey( # testing "tina can't spawn in player's hitbox"
                                           target=player, container=tinacontainer)
                            #tinacontainer.set_tina(tina) # in TinaFey.__init__ now
                            """for effect_ in player.effects: # completely
                                if effect_.name == 'repulsiveness': # unnessesary
                                    effect_.tina = tinacontainer""" # now
                        #if random.randint(0,3) < 2: # same
                        if random.random() > 0.45:
                            if tinacontainer.has_tina():
                                for i in range(random.randint(2, HARDNESS*2)):
                                    tinas.add(TinaFey(
                                        pos=(random.randint(0, scr_w),
                                             random.randint(0,scr_h)),
                                        do_dumb_pathfinding=True))
                                
                                # play sound effect
                                if random.random() > 0.1:
                                    bodydoubles_long.play()
                                else:
                                    bodydoubles_short.play()
                            else:
                                tinas.add(TinaFey(
                                        pos=(random.randint(0, scr_w),
                                             random.randint(0,scr_h))))
                                if random.random() < 0.1:
                                    bodydoubles_long.play()
                                else:
                                    bodydoubles_short.play()
                        else:
                            # play sound effect for single tina
                            so_many_tinafeys.play()
                        #tinacontainer.set_tina(TinaFey(target=player)) # THIS CAUSED MY SO MUCH COD DANG TROUBLE, so glad it's fixed
                    deathmsgs.flush() # each tick
                    """for particle in particles:
                        particle.update_logic()
                        if not particle.is_on_screen():
                            particle.kill('fell off the screen.')"""
                    for vfx in flags.vfx:
                        vfx.update_logic()
                        if not vfx.is_on_screen():
                            vfx.kill()
                    if random.random() > 0.9:
                        flags.vfx.add(Particle('bread', start_pos=(random.randint(-25, scr_w), -25), size=(44,44)))
                    
                    if random.random() < flags.level/10 or random.random() < flags.score / 1000:
                        if VERY_VERBOSE: print("\033[33mAdding extra AAMI because the player has gotten this far.\033[0m")
                        new_AAMI = AAMI((0,random.randint(0,scr_h)))
                        AAMIs.add(new_AAMI)
                        del new_AAMI
                    
                    if flags.level >= 1:
                        # do fancy 'level 2' things
                        if random.random() < 0.05:
                            try:
                                flags.doordack_orders.pop(0)
                            except IndexError: pass
                            else:
                                if random.random() < 0.98:
                                    flags.doordackers.add(DoorDacker((0, random.randint(0, scr_h))))
                                else:
                                    flags.snoops.add(SnoopDogg((random.randint(0, scr_w), random.randint(0, scr_h))))
                                    flags.levels[1].passed = True
                    # process snoops, do this after snoops are initially added, to give them one tick update before rendering
                    for snoop in flags.snoops:
                        snoop.update_logic()
                    profiler.end_section('tick')
                elif event.type == ADD_AAMI and not flags.paused:
                    # add an AAMI to the collection of AAMIs
                    new_AAMI = AAMI((0,random.randint(0,scr_h)))
                    AAMIs.add(new_AAMI)
                    del new_AAMI
                    # we also make an attempt to drop a hat for the player
                    # to catch and gain abilities from
                    if random.random() > 0.69:
                        #dropped_hat = Hat(random.randint(0,scr_w), 'top')
                        dropped_hat, hatevent = effect.get_hat(posx=random.randint(0, scr_w))
                        if DEBUG: flags.debugwindow.log_hatevent(hatevent)
                        falling_hats.add(dropped_hat)
                        effect.process_hat_event(hatevent)
                        if VERY_VERBOSE: print(f'\033[33mAdding hat {dropped_hat}. HatEvent: {bin(hatevent)}\033[0m')
                        del dropped_hat, hatevent
                elif event.type == GET_FPS:
                    print(f"FPS: {current_fps}", end='\r')
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        if flags.you_won:
                            pygame.mixer.music.stop()
                            AAMIs_crunched = flags.score
                            tinafey_likelihood = AAMIs_crunched + tinafey_likelihood # gets harder
                            flags.you_won = False
                            flags.score = AAMIs_crunched
                            if flags.levels[flags.level].passed: # if the present level has been passed
                                AAMIs_crunched -= 45 # basically resets the game, doesn't
                                flags.score    -= 45 # happen if the current level isn't passed
                                flags.level += 1 # level up!!! This will be used to get to higher levels in future...
                        else:
                            # future: change to open paused menu instead
                            # THE FUTURE IS NOW NOW
                            #flags.running = False
                            flags.paused = not flags.paused
                            flags.mainmenu.events_since_render += 1
                            #running = 0 # is `running` even still used? TODO: document and check (resolve to `flags.running` in future)
                    elif event.key == K_F3 and __debug__:
                        flags.show_hitboxes = not flags.show_hitboxes
                    elif event.key == K_SPACE:
                        flags.paused = not flags.paused
                        target_fps = 5 if flags.paused and GFX_MODE < 3 else FPS
                        flags.mainmenu.events_since_render += 1
                    elif event.key == K_z:
                        if (not player.dead) and (not flags.paused):
                            if player.currenthat is not None:
                                effect.process_hat_event(
                                    player.currenthat.activate_special_ability()
                                )
                            if flags['level'] >= 1:
                                flags.doordack_orders.append('1f53') # I had this idea that the content of
                                #                                    # this list could be unicode codepoints
                                #                                    # for food emojis which it would
                                #                                    # download and blit onto doordacker.surf on the fly
            profiler.end_section('event_processing')
            profiler.start_section('render')
            if not flags.paused:
                if DRAW_ON_SCREENSHOT:
                    scr.blit(backdrop, (0,0))
                else:
                    scr.fill((1,1,1)) # backdrop. Does loads for the vibe of the game :)
                
                profiler.start_section('render_entities')
                
                showrects = flags.show_hitboxes
                
                if flags.you_won: # do happy/walking texture on player
                    player.surf.fill((0,0,0,0))
                    player.surf.blit(pygame.transform.flip(player.walking1,
                                                           bool(player.direction), False), (0,0))
                scr.blit(player.surf, player.rect)
                if currenthat is not None:
                    scr.blit(currenthat.surf, currenthat.rect)
                    currenthat.update_pos()
                if showrects:
                    if currenthat is not None:
                        pygame.draw.rect(scr, (255, 1, 200), currenthat.rect, 1)
                    if player.crunching:
                        pygame.draw.rect(scr, (255,0,0), player.rect, 6)
                    pygame.draw.rect(scr, (0,254, 1), player.rect, 3)
                if not player.dead:
                    player.update_keypresses(pygame.key.get_pressed(), dt)
                player.update_pos()
                tina = tinacontainer.get_tina()
                if tinacontainer.has_tina():
                    tina.update_pos()
                    scr.blit(tina.surf, tina.rect)
                    if showrects:
                        pygame.draw.rect(scr, (245, 1, 0), tina.rect, 5)
                        pygame.draw.line(scr, (240, 120, 0), tina.rect.center,
                                        [tina.rect.centerx + tina.mv[0]*16, tina.rect.centery + tina.mv[1]*16],
                                        2)
                for aami in AAMIs:
                    scr.blit(aami.surf, aami.rect)
                    if showrects:
                        pygame.draw.rect(scr, (0,1,245), aami.rect, 2)
                    aami.update_pos()
                for doordacker in doordackers:
                    scr.blit(doordacker.surf, doordacker.rect)
                    if showrects:
                        pygame.draw.rect(scr, (245,1,0), doordacker.rect, 1)
                    doordacker.update_pos()
                    if not doordacker.is_on_screen():
                        doordacker.kill("(a doordacker) fell of the screen")
                for harmless_tina in tinas:
                    scr.blit(harmless_tina.surf, harmless_tina.rect) # caused much trouble...
                    if showrects:
                        pygame.draw.line(scr, (0, 120, 240), harmless_tina.rect.center,
                                        [harmless_tina.rect.centerx + harmless_tina.mv[0]*8,
                                         harmless_tina.rect.centery + harmless_tina.mv[1]*8],
                                        1)
                    harmless_tina.update_pos()
                
                # render snoop
                for snoop in flags.snoops:
                    snoop.update_pos()
                    scr.blit(snoop.surf, snoop.rect)
                    if showrects:
                        pygame.draw.rect(scr, (96, 1, 128), snoop.rect, 4)
                        pygame.draw.line(scr, (1, 128, 96), snoop.rect.center,
                                        [snoop.rect.centerx + snoop.mv[0]*8,
                                         snoop.rect.centery + snoop.mv[1]*8],
                                        1)

                """for particle in particles: # flags.vfx is now used instead
                    particle.update_pos()
                    particle.render(scr)"""
                for hat in falling_hats: # also caused much trouble
                    hat.update_pos()
                    scr.blit(hat.surf, hat.rect)
                    if showrects:
                        pygame.draw.rect(scr, (240,1,255), hat.rect, 4)
                paused_scr = scr.copy()
                profiler.end_section('render_entities')
            else:
                profiler.start_section('render_entities')
                scr.blit(paused_scr, (0,0))
                profiler.end_section('render_entities')
            for vfx in flags.vfx: # effects and particles, visual stuff that has no *real* logic
                vfx.render(scr, flags.show_hitboxes)
                vfx.update_pos()
            
            if VERY_VERBOSE:
                flags.debugwindow.update()
            
            renderscore(scr)
            if flags.you_won: scr.blit(you_won, (0,0))
            if player.crunched: scr.blit(you_died, (0,0))
            if SHOW_FPS: renderFPS(scr, current_fps)
            profiler.start_section('render_window')
            if RENDER_DEBUG_WINDOW: # render debug window
                debugwindow = flags.debugwindow
                debugwindow.update()
                scr.blit(debugwindow, (scr_w - (15 + debugwindow.width), scr_h - (15 + debugwindow.height)))
                del debugwindow
            if flags.paused:
                scr.blit(menus.darkener, (0,0))
                
                # render menu screen
                flags.mainmenu.update_gfx()
                scr.blit(flags.mainmenu, (0,0))
                
                if GFX_MODE > 2:
                    for vfx in flags.vfx:
                        if isinstance(vfx, Particle):
                            vfx.render(scr, False)
            profiler.end_section('render_window')
            pygame.display.flip()
            profiler.end_section('render')
            profiler.start_section('sleep')
            if flags.paused: menus.wait_for_event()
            dt = tiktok.tick(target_fps)
            profiler.end_section('total')
            profiler.end_section('sleep')
            if DEBUG and not VERY_VERBOSE: print(f"FPS: {current_fps}, {profiler.export_report(', ')}", end='\r')
        except KeyboardInterrupt:
            flags.running = False
            break
    
    deathmsgs.close()

    print('\n\033[0m')
    print(f"Score: {flags.score}, Level: {flags.level + 1}")
    pygame.quit()
    total_score = flags.score + flags.level*45
    print(f"So you crunched {total_score} AAMIs" + ('!' if flags.level >= 1 else ''))
    
    from sys import platform, exit, stdout
    if platform == 'win32':
        exit(0)

    # store high score
    import json
    highscore_loc = os.path.join(os.environ.get('HOME', './'), '.aami-crunching-highscore')
    if os.path.exists(highscore_loc):
        with open(highscore_loc) as f:
            try: d = json.loads(f.read())
            except json.JSONDecodeError: d = {'score':0, 'level':0}
        highscore = d['score'] + d['level']*45
        setby = d.get('user', 'a random guy from northcote')
        del d
    else:
        os.system('touch ' + highscore_loc)
        highscore = -1 # can't beat that for horribleness (at the game)
        setby = 'a random guy from northcote'
    
    if total_score > highscore:
        if stdout.isatty(): print("Which is a \033[1mHIGH SCORE!\033[0m")
        else: print("Which is a HIGH SCORE")
        with open(highscore_loc, 'w') as f:
            f.write(json.dumps({'score':flags.score, 'level':flags.level, 'user':os.environ.get('USER', 'guest')}))
    else:
        from pwd import getpwnam
        try: setBy = getpwnam(setby).pw_gecos
        except KeyError:
            setBy = setby
        print(f"The high score is {highscore}, set by {setBy}")

    if DEBUG:
        print(profiler.export_report())

    exit(0)
