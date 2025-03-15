" The AAMI crunching game. "

__lisence__ = 'Um the AAMI crunching game is a paid game (totally). ' # of course this is a joke, but I once had intensions to sell the game

"""
TODO:
- add status effects from hats [IN PROGRESS]
- REMOVE * IMPORTS TO MAKE LINTER HAPPY
"""

# pylint: disable=C0413
# pylint: disable=C0103
import os
import math
import random
import pygame
from pygame.locals import QUIT, KEYDOWN, USEREVENT, \
     K_ESCAPE, K_F3, K_z, \
     FULLSCREEN, SRCALPHA
import stuuf
from sprites import (
                     setflags,
                     load_deathmessage_log,
                     Entity,
                     Hat,
                     Player,
                     AAMI,
                     TinaFey,
                     Particle,
                     VisualEffect,
                     LightningBolt,
)
from settings import ( # so that all of the modules share the same constants...
                      HARDNESS,
                      FPS,
                      TITLE,
                      scr_w, scr_h,
                      scr_center,
                      tinafey_likelihood,
                      SHOW_FPS,
                      DEBUG,
                      VERY_VERBOSE,
                      VERSION,
                      RENDER_DEBUG_WINDOW,
)
import effect
import util

print(f"AAMI Crunching Game. version: {VERSION}")

current_fps = FPS # update sometimes I guess
scorestr = "Score: %02d"
fps_frmt = "FPS: %03f"
if DEBUG: tinafey_likelihood = 128 # makes tina VERY likely to spawn, for testing features involving tina
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
def rose_above(a1, a2, b): # been unused for ages, deprecating (removing) in next commit
    return (a1 <= b) and (not a2 < b)

if __name__ == '__main__':
    pygame.init()

    # open a window
    scr = pygame.display.set_mode((scr_w, scr_h))
    # set the window title
    pygame.display.set_caption('Loading... | %s' % TITLE)
    # and icon
    #pygame.display.set_icon(pygame.image.load(os.path.join(
    # and loading screen
    try:
        scr.blit(pygame.image.load(os.path.join('assets', 'loading.png')), (0,0))
        pygame.display.update()
    except FileNotFoundError as e:
        pygame.quit()
        print("ERROR: loading image not found. perhaps run from wrong directory.")
        print(f"Real Exception: {type(e).__name__}: {str(e)}")
        raise SystemExit(1)

    # state variables
    running = 1
    AAMIs_crunched = 0
    you_won_fname = ...
    winning_music = ...
    flags = stuuf.Flags(running=True, you_won=False, show_hitboxes=False, level=0)
    flags.running = running
    flags.score = AAMIs_crunched
    setflags(flags) # from sprites.py
    
    if DEBUG:
        import crunchDebug
        flags.debugwindow = crunchDebug.DebugWindow(flags)

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
    flags.tinatainer = tinacontainer
    AAMIs = pygame.sprite.Group()
    tinas = pygame.sprite.Group()
    falling_hats = pygame.sprite.Group()
    particles = pygame.sprite.Group()
    visualEffects = pygame.sprite.Group()
    flags.AAMIs = AAMIs
    flags.tinas = tinas
    flags.vfx = visualEffects # which includes particles now

    
    # test effects
    if DEBUG and TEST_EFFECTS:
         e = effect.BaseAAMIAtrractor(player, level=1, aamis=AAMIs)
         e.apply_once()
         player.effects.append(e)
    
    # you won screen
    you_won  = ...
    you_died = pygame.image.load(os.path.join('assets', 'you_died.png')).convert_alpha()

    # clock
    tiktok = pygame.time.Clock()

    pygame.display.set_caption(TITLE)

    while running:
        tina = tinacontainer.get_tina()
        try:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = 0
                    flags.running = False
                elif event.type == GAME_TICK:
                    # do game tick stuff
                    if DEBUG: player.update_logic(particles)
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
                            if aami.rect.colliderect(tina.rect) and (random.random() > 0.45):
                                aami.crunched = True
                                aami.crunchedBy = 'TinaFey'
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
                        print(f"AAMIs crunched: {AAMIs_crunched}")
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
                        # 'You Won' screen and level up.
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
                    for particle in particles:
                        particle.update_logic()
                        if not particle.is_on_screen():
                            particle.kill('fell off the screen.')
                    for vfx in flags.vfx: vfx.update_logic()
                    if DEBUG: flags.debugwindow.update()
                    current_fps = tiktok.get_fps()
                elif event.type == ADD_AAMI:
                    # add an AAMI to the collection of AAMIs
                    new_AAMI = AAMI((0,random.randint(0,scr_h)))
                    AAMIs.add(new_AAMI)
                    del new_AAMI
                    # we also make an attempt to drop a hat for the player
                    # to catch and gain abilities from
                    if random.random() > 0.69:
                        #dropped_hat = Hat(random.randint(0,scr_w), 'top')
                        dropped_hat, hatevent = effect.get_hat(posx=random.randint(0, scr_w))
                        effect.process_hat_event(hatevent)
                        if DEBUG: flags.debugwindow.log_hatevent(hatevent)
                        falling_hats.add(dropped_hat)
                        if VERY_VERBOSE: print(f'Adding hat {dropped_hat}. HatEvent: {bin(hatevent)}')
                        del dropped_hat, hatevent
                elif event.type == GET_FPS:
                    pass
                    print(f"FPS: {current_fps}", end='\r')
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        if flags.you_won:
                            pygame.mixer.music.stop()
                            AAMIs_crunched = flags.score
                            tinafey_likelihood = AAMIs_crunched + tinafey_likelihood # gets harder
                            AAMIs_crunched -= 45 # basically resets the game
                            flags.you_won = False
                            flags.score = AAMIs_crunched
                            flags.level += 1 # level up!!! This will be used to get to higher levels in future...
                        else:
                            flags.running = False
                            running = 0
                    elif event.key == K_F3 and __debug__:
                        flags.show_hitboxes = not flags.show_hitboxes
                    elif event.key == K_z:
                        if not player.dead and player.currenthat is not None: # if the player is not dead
                            effect.process_hat_event(
                                player.currenthat.activate_special_ability()
                            ) # to avoid super long line, this is on multiple lines
                """elif event.type == RESET: # doesn't happen, removed for omtimisation reasons
                    AAMIs_crunched = 1
                    flags = stuuf.Flags(running=True, you_won=False)
                    #next_AAMI_speed = 6"""
            scr.fill((1,1,1))
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
                player.update_keypresses(pygame.key.get_pressed())
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
            for harmless_tina in tinas:
                scr.blit(harmless_tina.surf, harmless_tina.rect) # caused much trouble...
                if showrects:
                    pygame.draw.line(scr, (0, 120, 240), harmless_tina.rect.center,
                                    [harmless_tina.rect.centerx + harmless_tina.mv[0]*8,
                                     harmless_tina.rect.centery + harmless_tina.mv[1]*8],
                                    1)
                harmless_tina.update_pos()
            for particle in particles:
                particle.update_pos()
                particle.render(scr)
            for hat in falling_hats: # also caused much trouble
                hat.update_pos()
                scr.blit(hat.surf, hat.rect)
                if showrects:
                    pygame.draw.rect(scr, (240,1,255), hat.rect, 4)
            for vfx in flags.vfx:
                vfx.render(scr, flags.show_hitboxes)
                vfx.update_pos()
                if not vfx.is_on_screen():
                    vfx.kill()
            
            if VERY_VERBOSE:
                flags.debugwindow.update()
            
            renderscore(scr)
            if flags.you_won: scr.blit(you_won, (0,0))
            if player.crunched: scr.blit(you_died, (0,0))
            if SHOW_FPS: renderFPS(scr, current_fps)
            if RENDER_DEBUG_WINDOW: # render debug window
                debugwindow = flags.debugwindow
                scr.blit(debugwindow, (scr_w - (15 + debugwindow.width), scr_h - (15 + debugwindow.height)))
                del debugwindow
            pygame.display.flip()
            tiktok.tick(FPS)
        except KeyboardInterrupt:
            flags.running = False
            break
    
    deathmsgs.close()

    print('\n')
    print(f"Score: {flags.score}, Level: {flags.level + 1}")
    print(f"So you crunched {flags.score + flags.level*45} AAMIs" + ('!' if flags.level >= 1 else ''))
    
    pygame.quit()
    quit()
