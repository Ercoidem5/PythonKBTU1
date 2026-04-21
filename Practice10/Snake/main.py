import pygame
import random

pygame.init()

WIDTH, HEIGHT = 600, 600
CELL = 20

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 32)

snake = [(300, 300), (280, 300), (260, 300)]
direction = (20, 0)

food = None
score = 0
level = 1
speed = 7

def spawn_food():
    while True:
        x = random.randrange(0, WIDTH, CELL)
        y = random.randrange(0, HEIGHT, CELL)
        if (x, y) not in snake:
            return (x, y)

food = spawn_food()

running = True
while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and direction != (0, CELL):
        direction = (0, -CELL)
    if keys[pygame.K_DOWN] and direction != (0, -CELL):
        direction = (0, CELL)
    if keys[pygame.K_LEFT] and direction != (CELL, 0):
        direction = (-CELL, 0)
    if keys[pygame.K_RIGHT] and direction != (-CELL, 0):
        direction = (CELL, 0)

    head_x = snake[0][0] + direction[0]
    head_y = snake[0][1] + direction[1]
    new_head = (head_x, head_y)

    if head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT:
        running = False

    if new_head in snake:
        running = False

    snake.insert(0, new_head)

    if new_head == food:
        score += 1
        food = spawn_food()
    else:
        snake.pop()

    if score // 4 + 1 > level:
        level = score // 4 + 1
        speed += 2

    for segment in snake:
        pygame.draw.rect(screen, (0, 255, 0), (*segment, CELL, CELL))

    pygame.draw.rect(screen, (255, 0, 0), (*food, CELL, CELL))

    score_text = font.render("Score: " + str(score), True, (255, 255, 255))
    level_text = font.render("Level: " + str(level), True, (255, 255, 255))

    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 40))

    pygame.display.flip()
    clock.tick(speed)

pygame.quit()