from menus import MainMenu
from settings import *

import pygame
from pygame.locals import K_ESCAPE

scr = pygame.display.set_mode((scr_w, scr_h))

run = True
fps = 60

clk = pygame.time.Clock()
menu= MainMenu()
menu.build_contents()

while run:
    clk.tick(fps)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:
                run = False
        if event.type != pygame.MOUSEMOTION:
            print("Event:", event.type, event.dict)
        menu.process_event(event)
    scr.fill((15,150,250))
    keys = pygame.key.get_pressed()
    menu.update_gfx()
    scr.blit(menu, (0,0))
    pygame.display.flip()
    #print("FPS:", clk.get_fps(), ' '*10, end='\r')

pygame.quit()
