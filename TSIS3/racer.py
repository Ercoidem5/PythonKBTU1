import pygame, random
from persistence import *
from ui import draw_menu, draw_settings, draw_game_over, draw_leaderboard

WIDTH, HEIGHT = 400, 600
LANES = [60, 140, 220, 300]
BLACK = (20, 20, 20)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)



car = None
enemy = []
coins = []
powerups = []
active_power = None
power_timer = 0
shield_active = False
score = 0
distance = 0
coin_score = 0
spawn_timer = 0
state = "menu"
settings = None

typing_name = False
name_buffer = ""

# init 
def reset_game():
    global car, enemy, coins, score, distance, coin_score, spawn_timer
    car = pygame.Rect(180, 500, 40, 60)
    enemy = []
    coins = []
    score = 0
    distance = 0
    coin_score = 0
    spawn_timer = 0


def spawn_objects():
    enemy.append(pygame.Rect(random.choice(LANES), -60, 40, 60))
    coins.append(pygame.Rect(random.choice(LANES) + 10, -20, 20, 20))
    if random.random() < 0.2:
        kind = random.choice(["nitro", "shield", "repair"])
        powerups.append({
            "rect": pygame.Rect(random.choice(LANES)+8, -20, 24, 24),
            "type": kind,
            "ttl": 300  # время жизни
        })


# game update
def update_game():
    global score, distance, coin_score, spawn_timer, state
    global active_power, power_timer, shield_active

    keys = pygame.key.get_pressed()

    # ---------------- SPEED (nitro) ----------------
    speed = 5
    if active_power == "nitro":
        if pygame.time.get_ticks() < power_timer:
            speed = 9
        else:
            active_power = None

    if keys[pygame.K_LEFT]:
        car.x = max(0, car.x - speed)
    if keys[pygame.K_RIGHT]:
        car.x = min(WIDTH - 40, car.x + speed)

    # ---------------- SCORE ----------------
    distance += 1
    score = coin_score + distance // 10

    # ---------------- SPAWN ----------------
    spawn_timer += 1
    if spawn_timer > 50:
        spawn_objects()
        spawn_timer = 0

    # ---------------- POWERUPS ----------------
    for p in powerups[:]:
        p["rect"].y += 5
        p["ttl"] -= 1

        if p["rect"].colliderect(car):
            active_power = p["type"]

            if p["type"] == "nitro":
                power_timer = pygame.time.get_ticks() + 4000

            elif p["type"] == "shield":
                shield_active = True

            elif p["type"] == "repair":
                shield_active = True  # можно улучшить

            powerups.remove(p)

        elif p["ttl"] <= 0 or p["rect"].y > HEIGHT:
            powerups.remove(p)

    # ---------------- ENEMIES ----------------
    for e in enemy[:]:
        e.y += 5

        if e.colliderect(car):
            if shield_active:
                shield_active = False
                active_power = None
                enemy.remove(e)
                continue
            else:
                add_score({
                    "name": settings["username"],
                    "score": score,
                    "distance": distance
                })
                state = "over"

        if e.y > HEIGHT:
            enemy.remove(e)

    # ---------------- COINS ----------------
    for c in coins[:]:
        c.y += 5

        if c.colliderect(car):
            coin_score += 1
            coins.remove(c)

        elif c.y > HEIGHT:
            coins.remove(c)

# draw game
def draw_game(screen, font):
    screen.fill(BLACK)

    pygame.draw.rect(screen, settings["car_color"], car)

    for e in enemy:
        pygame.draw.rect(screen, RED, e)

    for c in coins:
        pygame.draw.ellipse(screen, YELLOW, c)

    for p in powerups:
        color = {
            "nitro": (0,255,0),
            "shield": (0,0,255),
            "repair": (255,255,255)
        }[p["type"]]

        pygame.draw.rect(screen, color, p["rect"])
    screen.blit(font.render(f"Score: {score}", True, (255, 255, 255)), (10, 10))
    screen.blit(font.render(f"Distance: {distance}", True, (255, 255, 255)), (10, 40))

    if active_power:
        if active_power == "nitro":
            remaining = max(0, (power_timer - pygame.time.get_ticks()) // 1000)
            text = f"Power: Nitro ({remaining}s)"
        else:
            text = f"Power: {active_power}"

        screen.blit(font.render(text, True, (255,255,255)), (10, 70))


# main loop
def run():
    global state, settings
    global typing_name, name_buffer
        
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 32)
    big = pygame.font.SysFont(None, 48)

    settings = load_settings()
    reset_game()

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and typing_name:
                if event.key == pygame.K_RETURN:
                    settings["username"] = name_buffer
                    save_settings(settings)
                    typing_name = False
                elif event.key == pygame.K_BACKSPACE:
                    name_buffer = name_buffer[:-1]
                else:
                    if len(name_buffer) < 12:
                        name_buffer += event.unicode
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos

                # ---------------- MENU ----------------
                if state == "menu":
                    btns = draw_menu(screen, font, big)
                    if btns[0].clicked(pos):
                        reset_game()
                        state = "game"
                    elif btns[1].clicked(pos):
                        state = "board"
                    elif btns[2].clicked(pos):
                        state = "settings"
                    elif btns[3].clicked(pos):
                        running = False

                # settings
                elif state == "settings":
                    btns = draw_settings(screen, font, big,
                                         settings["sound"],
                                         settings["car_color"],
                                         settings["difficulty"],
                                         settings["username"])

                    if btns[0].clicked(pos):
                        settings["sound"] = not settings["sound"]

                    elif btns[1].clicked(pos):
                        colors = [[0,0,255],[255,0,0],[0,255,0]]
                        i = colors.index(settings["car_color"]) if settings["car_color"] in colors else 0
                        settings["car_color"] = colors[(i+1)%3]

                    elif btns[2].clicked(pos):
                        diff = ["easy","normal","hard"]
                        i = diff.index(settings["difficulty"])
                        settings["difficulty"] = diff[(i+1)%3]

                    elif btns[3].clicked(pos):  # Name button
                        typing_name = True
                        name_buffer = settings["username"]
                    elif btns[4].clicked(pos):  # Back
                        state = "menu"
                    save_settings(settings)

                # game over
                elif state == "over":
                    btns = draw_game_over(screen, font, big, score, distance, coin_score)
                    if btns[0].clicked(pos):
                        reset_game()
                        state = "game"
                    elif btns[1].clicked(pos):
                        state = "menu"

                # leaderboard
                elif state == "board":
                    back = draw_leaderboard(screen, font, big, load_scores())
                    if back.clicked(pos):
                        state = "menu"

        # render states
        if state == "menu":
            draw_menu(screen, font, big)

        elif state == "settings":
            current_name = name_buffer if typing_name else settings["username"]

            draw_settings(screen, font, big,
                        settings["sound"],
                        settings["car_color"],
                        settings["difficulty"],
                        current_name)

        elif state == "board":
            draw_leaderboard(screen, font, big, load_scores())

        elif state == "over":
            draw_game_over(screen, font, big, score, distance, coin_score)

        elif state == "game":
            update_game()
            draw_game(screen, font)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
