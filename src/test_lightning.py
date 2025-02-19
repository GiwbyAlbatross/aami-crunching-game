import pygame

import sprites
import stuuf

scr = pygame.display.set_mode([1280, 1080])
aami = sprites.AAMI((200, 728))
lightning = sprites.LightningBolt(aami.rect)

flags = stuuf.Flags(you_won=False)
sprites.setflags(flags)

run = 1
clk = pygame.time.Clock()

while run:
    clk.tick(60)
    print('FPS:', clk.get_fps(), end='\r')
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = 0
        elif event.type == pygame.KEYDOWN:
            run = 0
    scr.fill((0,0,0))
    scr.blit(aami.surf, aami.rect)
    lightning.update_pos()
    lightning.render(scr, True)
    pygame.display.update()
