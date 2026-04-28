import pygame
import random
import json
from config import *
from db import save_game, get_best

# --- INIT ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 24)

# --- SETTINGS ---
with open("settings.json") as f:
    settings = json.load(f)

snake_color = tuple(settings["snake_color"])
grid = settings["grid"]

def input_username(screen):
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 32)

    username = ""
    active = True

    while active:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username.strip():
                    return username

                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]

                else:
                    # фильтр: только нормальные символы
                    if len(username) < 15 and event.unicode.isprintable():
                        username += event.unicode

        title = font.render("Enter Username", True, (255, 255, 255))
        text = font.render(username, True, (0, 255, 0))
        hint = small_font.render("Press ENTER to continue", True, (150,150,150))

        screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 300))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, 380))

        pygame.display.flip()



# --- USER ---
username = input_username(screen)
best_score = get_best(username)

# --- GAME STATE ---
snake = [(300,300),(280,300),(260,300)]
direction = (CELL,0)

score = 0
level = 1
speed = 7

food = None
poison = None
power = None
power_spawn_time = 0
active_power = None
power_timer = 0

obstacles = []

# --- FUNCTIONS ---
def spawn_food():
    while True:
        x = random.randrange(0, WIDTH, CELL)
        y = random.randrange(0, HEIGHT, CELL)
        if (x,y) not in snake and (x,y) not in obstacles:
            return (x,y)

def spawn_power():
    types = ["speed", "slow", "shield"]
    return {"pos": spawn_food(), "type": random.choice(types)}



def spawn_obstacles():
    global obstacles
    obstacles = []
    for _ in range(10):
        obstacles.append(spawn_food())

# --- INIT FOOD ---
food = spawn_food()

# --- GAME LOOP ---
running = True
while running:
    screen.fill((0,0,0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()


    if keys[pygame.K_UP] and direction!=(0,CELL):
        direction=(0,-CELL)
    if keys[pygame.K_DOWN] and direction!=(0,-CELL):
        direction=(0,CELL)
    if keys[pygame.K_LEFT] and direction!=(CELL,0):
        direction=(-CELL,0)
    if keys[pygame.K_RIGHT] and direction!=(-CELL,0):
        direction=(CELL,0)

    head = (snake[0][0]+direction[0],
            snake[0][1]+direction[1])

    # --- COLLISION ---
    if head in snake or head in obstacles:
        if active_power == "shield":
            active_power = None
        else:
            break

    if head[0]<0 or head[0]>=WIDTH or head[1]<0 or head[1]>=HEIGHT:
        if active_power == "shield":
            active_power = None
        else:
            break

    snake.insert(0, head)

    # --- FOOD ---
    if head == food:
        score += 1
        food = spawn_food()
    else:
        snake.pop()

    # --- POISON ---
    if poison and head == poison:
        for _ in range(2):
            if len(snake) > 1:
                snake.pop()
        if len(snake) <= 1:
            break
        poison = None

    # --- POWER ---
    if power and head == power["pos"]:
        active_power = power["type"]
        power_timer = pygame.time.get_ticks()
        power = None

    if active_power:
        if pygame.time.get_ticks() - power_timer > 5000:
            active_power = None

    # --- SPAWN LOGIC ---
    if random.random() < 0.01 and not poison:
        poison = spawn_food()

    if not power and random.random() < 0.01:
        power = spawn_power()
        power_spawn_time = pygame.time.get_ticks()

    if power and pygame.time.get_ticks() - power_spawn_time > 8000:
        power = None

    # --- LEVEL ---
    if score // 5 + 1 > level:
        level += 1
        speed += 1
        if level >= 3:
            spawn_obstacles()

    # --- DRAW GRID ---
    if grid:
        for x in range(0, WIDTH, CELL):
            pygame.draw.line(screen,(40,40,40),(x,0),(x,HEIGHT))
        for y in range(0, HEIGHT, CELL):
            pygame.draw.line(screen,(40,40,40),(0,y),(WIDTH,y))

    # --- DRAW SNAKE ---
    for s in snake:
        pygame.draw.rect(screen, snake_color, (*s, CELL, CELL))

    # --- DRAW FOOD ---
    pygame.draw.rect(screen, (255,0,0), (*food, CELL, CELL))

    if poison:
        pygame.draw.rect(screen, (139,0,0), (*poison, CELL, CELL))

    if power:
        pygame.draw.rect(screen, (0,255,255), (*power["pos"], CELL, CELL))

    for o in obstacles:
        pygame.draw.rect(screen, (100,100,100), (*o, CELL, CELL))

    # --- UI ---
    texts = [
        f"Score: {score}",
        f"Level: {level}",
        f"Best: {best_score}"
    ]

    for i, t in enumerate(texts):
        screen.blit(font.render(t, True, (255,255,255)), (10, 10 + i*20))

    pygame.display.flip()
    clock.tick(speed)

# --- SAVE RESULT ---
save_game(username, score, level)

pygame.quit()