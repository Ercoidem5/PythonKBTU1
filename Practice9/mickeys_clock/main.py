import pygame
import sys
from clock import draw_clock

pygame.init()

WIDTH, HEIGHT = 870, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Clock")

background = pygame.image.load("images/mickeyclock.jpeg").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.blit(background, (0, 0))
    draw_clock(screen, WIDTH, HEIGHT)

    pygame.display.flip()
    clock.tick(60)