import pygame
import sys
import os
from player import Player

pygame.init()

WIDTH = 600
HEIGHT = 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Music Player")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
ACCENT = (0, 200, 120)
LIGHT_GRAY = (160, 160, 160)

font = pygame.font.SysFont("monospace", 18)

MUSIC_FOLDER = os.path.join(os.path.dirname(__file__), "music")
player = Player(MUSIC_FOLDER)

clock = pygame.time.Clock()

controls = [
"[P] Play / Resume",
"[S] Stop",
"[SPACE] Pause",
"[N] Next track",
"[B] Previous track",
"[Q] Quit",
]

running = True
while running:
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_p:
                player.play()
            elif event.key == pygame.K_s:
                player.stop()
            elif event.key == pygame.K_SPACE:
                player.pause()
            elif event.key == pygame.K_n:
                player.next_track()
            elif event.key == pygame.K_b:
                player.prev_track()

    if player.is_track_finished():
        player.next_track()


    track_label = font.render("NOW PLAYING", True, LIGHT_GRAY)
    screen.blit(track_label, (40, 90))

    track_name = player.get_track_name()
    track_text = font.render(track_name, True, WHITE)
    screen.blit(track_text, (40, 115))

    if player.playing and not player.paused:
        status_text = "PLAYING"
        status_color = ACCENT
    elif player.paused:
        status_text = "PAUSED"
        status_color = (255, 200, 0)
    else:
        status_text = "STOPPED"
        status_color = LIGHT_GRAY

    status = font.render(status_text, True, status_color)
    screen.blit(status, (40, 155))

    pos_label = font.render("TIME: " + player.get_pos(), True, LIGHT_GRAY)
    screen.blit(pos_label, (40, 185))

    if player.tracks:
        idx_text = font.render(
            f"TRACK {player.index + 1} / {len(player.tracks)}", True, LIGHT_GRAY
        )
        screen.blit(idx_text, (WIDTH - idx_text.get_width() - 40, 185))

    for i, line in enumerate(controls):
        ctrl = font.render(line, True, LIGHT_GRAY)
        screen.blit(ctrl, (40, 258 + i * 20))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()