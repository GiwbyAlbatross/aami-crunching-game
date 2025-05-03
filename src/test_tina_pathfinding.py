from sprites import Entity, SnoopDogg
from settings import *

import pygame
from pygame.locals import K_SPACE, K_TAB, K_ESCAPE

scr = pygame.display.set_mode((scr_w, scr_h))

run = True
mvlen = 10
fps = 60

clk = pygame.time.Clock()

entity = Entity()
tina = SnoopDogg() # oh dear.

been = pygame.Surface((scr_w, scr_h), pygame.SRCALPHA)
been.fill([0,0,0,0])

pathfinder = tina.dumbpathfinding
pathfinder.target = pathfinder._generate_target_coords()

while run:
    clk.tick(fps)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:
                run = False
    scr.fill((100,100,100))
    keys = pygame.key.get_pressed()
    if keys[K_SPACE]:
        tina.update_pos()
    if keys[K_TAB]:
        print("\nUpdating logic")
        tina.update_logic()
        tina.update_pos()
    scr.blit(been, (0,0))
    scr.blit(tina.surf, tina.rect)
    pygame.draw.circle(scr, (250,25,0), pathfinder.target, 8)
    pygame.draw.circle(been, (1,1,1), tina.rect.center, 3)
    print(pathfinder.mv, tina.mv, end='\r')
    pygame.draw.rect(scr, (1,0,240), tina.rect, 5)
    pygame.draw.aaline(scr, (255,24,2), tina.rect.center,
        (tina.rect.centerx + tina.mv[0]*mvlen, tina.rect.centery + tina.mv[1]*mvlen), 8)
    pygame.display.flip()

pygame.quit()
