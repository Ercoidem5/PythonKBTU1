import pygame
import game
from db import init_db, get_top10

pygame.init()
screen = pygame.display.set_mode((600, 600))

init_db()


# ---------- USERNAME ----------
def input_username():
    font = pygame.font.SysFont(None, 40)
    name = ""

    while True:
        screen.fill((0, 0, 0))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN and name.strip():
                    return name
                elif e.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 15:
                        name += e.unicode

        txt = font.render("Name: " + name, True, (255, 255, 255))
        screen.blit(txt, (100, 250))

        pygame.display.flip()


# ---------- LEADERBOARD ----------
def show_leaderboard():
    data = get_top10()
    font = pygame.font.SysFont(None, 30)

    while True:
        screen.fill((0, 0, 0))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                exit()
            if e.type == pygame.KEYDOWN:
                return

        title = font.render("Leaderboard", True, (255,255,255))
        screen.blit(title, (200, 20))

        for i, row in enumerate(data):
            text = f"{i+1}. {row[0]}  Score:{row[1]}  Lvl:{row[2]}"
            screen.blit(font.render(text, True, (255, 255, 255)), (50, 80 + i * 30))

        hint = font.render("Press any key to go back", True, (150,150,150))
        screen.blit(hint, (120, 550))

        pygame.display.flip()


# ---------- MAIN MENU ----------
def main_menu():
    font = pygame.font.SysFont(None, 48)

    while True:
        screen.fill((0, 0, 0))

        title = font.render("SNAKE", True, (255,255,255))
        play = font.render("P - Play", True, (200,200,200))
        leaderboard = font.render("L - Leaderboard", True, (200,200,200))
        quit_txt = font.render("Q - Quit", True, (200,200,200))

        screen.blit(title, (240, 150))
        screen.blit(play, (220, 250))
        screen.blit(leaderboard, (160, 320))
        screen.blit(quit_txt, (220, 390))

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


# ---------- GAME OVER ----------
def game_over_screen(score, level):
    font = pygame.font.SysFont(None, 48)

    while True:
        screen.fill((0, 0, 0))

        text = font.render("Game Over", True, (255,255,255))
        score_txt = font.render(f"Score: {score}", True, (200,200,200))
        lvl_txt = font.render(f"Level: {level}", True, (200,200,200))

        hint = font.render("M - Menu | L - Leaderboard", True, (150,150,150))

        screen.blit(text, (200, 200))
        screen.blit(score_txt, (220, 260))
        screen.blit(lvl_txt, (220, 310))
        screen.blit(hint, (100, 380))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_m:
                    return "menu"
                if e.key == pygame.K_l:
                    return "leaderboard"


# ---------- MAIN ----------
def main():
    username = input_username()

    running = True

    while running:
        action = main_menu()

        if action == "quit":
            break

        if action == "leaderboard":
            show_leaderboard()
            continue

        if action == "play":
            score, level = game.run(screen, username)
            game.save_result(username, score, level)

            after = game_over_screen(score, level)

            if after == "leaderboard":
                show_leaderboard()
            elif after == "quit":
                running = False


main()