import pygame
from db import init_db, get_top10
import game

pygame.init()
screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Snake")

init_db()


# INPUT USERNAME
def input_username():
    font = pygame.font.SysFont(None, 48)
    small = pygame.font.SysFont(None, 32)
    name = ""

    while True:
        screen.fill((0, 0, 0))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif e.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 15 and e.unicode.isprintable():
                        name += e.unicode

        title = font.render("Enter Username", True, (255, 255, 255))
        txt   = font.render(name, True, (0, 255, 0))
        hint  = small.render("Press ENTER to continue", True, (150, 150, 150))

        screen.blit(title, (300 - title.get_width() // 2, 200))
        screen.blit(txt,   (300 - txt.get_width() // 2,   300))
        screen.blit(hint,  (300 - hint.get_width() // 2,  380))

        pygame.display.flip()


# LEADERBOARD
def show_leaderboard():
    data = get_top10()
    font = pygame.font.SysFont(None, 30)

    while True:
        screen.fill((0, 0, 0))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                exit()
            if e.type == pygame.KEYDOWN:
                return

        title = font.render("Leaderboard", True, (255, 255, 255))
        screen.blit(title, (300 - title.get_width() // 2, 20))

        for i, row in enumerate(data):
            text = f"{i+1}. {row[0]}  Score: {row[1]}  Lvl: {row[2]}"
            screen.blit(font.render(text, True, (255, 255, 255)), (50, 70 + i * 30))

        hint = font.render("Press any key to go back", True, (150, 150, 150))
        screen.blit(hint, (300 - hint.get_width() // 2, 550))

        pygame.display.flip()


# MAIN MENU
def main_menu():
    font  = pygame.font.SysFont(None, 56)
    small = pygame.font.SysFont(None, 38)

    while True:
        screen.fill((0, 0, 0))

        items = [
            (font,  "SNAKE",             (255, 255, 255), 140),
            (small, "P  —  Play",        (200, 200, 200), 250),
            (small, "L  —  Leaderboard", (200, 200, 200), 310),
            (small, "Q  —  Quit",        (200, 200, 200), 370),
        ]
        for f, text, color, y in items:
            surf = f.render(text, True, color)
            screen.blit(surf, (300 - surf.get_width() // 2, y))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_p:
                    return "play"
                if e.key == pygame.K_l:
                    return "leaderboard"
                if e.key == pygame.K_q:
                    return "quit"


# GAME OVER SCREEN
def game_over_screen(score, level):
    font  = pygame.font.SysFont(None, 56)
    small = pygame.font.SysFont(None, 36)

    while True:
        screen.fill((0, 0, 0))

        lines = [
            (font,  "Game Over",                  (255, 255, 255), 180),
            (small, f"Score: {score}",            (200, 200, 200), 260),
            (small, f"Level:  {level}",           (200, 200, 200), 300),
            (small, "M — Menu   L — Leaderboard", (150, 150, 150), 380),
        ]
        for f, text, color, y in lines:
            surf = f.render(text, True, color)
            screen.blit(surf, (300 - surf.get_width() // 2, y))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_m:
                    return "menu"
                if e.key == pygame.K_l:
                    return "leaderboard"


# MAIN
def main():
    username = input_username()

    while True:
        action = main_menu()

        if action == "quit":
            break

        if action == "play":
            score, level = game.run(screen, username)
            game.save_result(username, score, level)

            after = game_over_screen(score, level)

            if after == "leaderboard":
                show_leaderboard()
            elif after == "quit":
                break

        if action == "leaderboard":
            show_leaderboard()

    pygame.quit()


main()