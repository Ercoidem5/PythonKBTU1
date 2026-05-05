import pygame
import random
import json
from config import *
from db import save_game, get_best

# LOAD SETTINGS
with open("settings.json") as f:
    settings = json.load(f)

snake_color = tuple(settings["snake_color"])
grid = settings["grid"]

font_small = None


# FUNCTIONS
def spawn_food(snake, obstacles):
    while True:
        x = random.randrange(0, WIDTH, CELL)
        y = random.randrange(0, HEIGHT, CELL)
        if (x, y) not in snake and (x, y) not in obstacles:
            return (x, y)


def spawn_power(snake, obstacles):
    types = ["speed", "slow", "shield"]
    return {"pos": spawn_food(snake, obstacles), "type": random.choice(types)}


def spawn_obstacles(snake):
    obstacles = []
    for _ in range(10):
        obstacles.append(spawn_food(snake, obstacles))
    return obstacles


def draw_grid(screen):
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(screen, (40, 40, 40), (0, y), (WIDTH, y))


# MAIN GAME FUNCTION
def run(screen, username):
    global font_small
    font_small = pygame.font.SysFont(None, 24)

    clock = pygame.time.Clock()

    best_score = get_best(username)

    # GAME STATE
    snake = [(300, 300), (280, 300), (260, 300)]
    direction = (CELL, 0)

    score = 0
    level = 1
    speed = 7

    food = spawn_food(snake, [])
    poison = None
    power = None
    power_spawn_time = 0
    active_power = None
    power_timer = 0
    obstacles = []

    running = True
    while running:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        keys = pygame.key.get_pressed()

        # DIRECTION CONTROL
        if keys[pygame.K_UP] and direction != (0, CELL):
            direction = (0, -CELL)
        if keys[pygame.K_DOWN] and direction != (0, -CELL):
            direction = (0, CELL)
        if keys[pygame.K_LEFT] and direction != (CELL, 0):
            direction = (-CELL, 0)
        if keys[pygame.K_RIGHT] and direction != (-CELL, 0):
            direction = (CELL, 0)

        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

        # COLLISION WITH SELF OR OBSTACLES
        if head in snake or head in obstacles:
            if active_power == "shield":
                active_power = None
            else:
                break

        # COLLISION WITH WALLS
        if head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT:
            if active_power == "shield":
                active_power = None
            else:
                break

        snake.insert(0, head)

        # FOOD
        if head == food:
            score += 1
            food = spawn_food(snake, obstacles)
        else:
            snake.pop()

        # POISON
        if poison and head == poison:
            for _ in range(2):
                if len(snake) > 1:
                    snake.pop()
            if len(snake) <= 1:
                break
            poison = None

        # POWERUP PICKUP
        if power and head == power["pos"]:
            active_power = power["type"]
            power_timer = pygame.time.get_ticks()
            power = None

        # POWERUP EXPIRY
        if active_power:
            if pygame.time.get_ticks() - power_timer > 5000:
                active_power = None

        # SPAWN LOGIC
        if random.random() < 0.01 and not poison:
            poison = spawn_food(snake, obstacles)

        if not power and random.random() < 0.01:
            power = spawn_power(snake, obstacles)
            power_spawn_time = pygame.time.get_ticks()

        if power and pygame.time.get_ticks() - power_spawn_time > 8000:
            power = None

        # LEVEL UP
        if score // 5 + 1 > level:
            level += 1
            speed += 1
            if level >= 3:
                obstacles = spawn_obstacles(snake)

        # DRAW GRID
        if grid:
            draw_grid(screen)

        # DRAW SNAKE
        for s in snake:
            pygame.draw.rect(screen, snake_color, (*s, CELL, CELL))

        # DRAW FOOD
        pygame.draw.rect(screen, (255, 0, 0), (*food, CELL, CELL))

        if poison:
            pygame.draw.rect(screen, (139, 0, 0), (*poison, CELL, CELL))

        if power:
            pygame.draw.rect(screen, (0, 255, 255), (*power["pos"], CELL, CELL))

        for o in obstacles:
            pygame.draw.rect(screen, (100, 100, 100), (*o, CELL, CELL))

        # UI
        texts = [
            f"Score: {score}",
            f"Level: {level}",
            f"Best:  {best_score}"
        ]
        for i, t in enumerate(texts):
            screen.blit(font_small.render(t, True, (255, 255, 255)), (10, 10 + i * 20))

        pygame.display.flip()
        clock.tick(speed)

    return score, level


def save_result(username, score, level):
    save_game(username, score, level)