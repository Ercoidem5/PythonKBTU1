import pygame
import random

pygame.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

car = pygame.Rect(180, 500, 40, 60)
coins = []
coin_timer = 0
score = 0

font = pygame.font.SysFont(None, 36)

running = True
while running:
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and car.x > 0:
        car.x -= 5
    if keys[pygame.K_RIGHT] and car.x < WIDTH - car.width:
        car.x += 5

    coin_timer += 1
    if coin_timer > 40:
        coin = pygame.Rect(random.randint(0, WIDTH - 20), -20, 20, 20)
        coins.append(coin)
        coin_timer = 0

    for coin in coins[:]:
        coin.y += 5
        if coin.colliderect(car):
            coins.remove(coin)
            score += 1
        elif coin.y > HEIGHT:
            coins.remove(coin)

    pygame.draw.rect(screen, (0, 0, 255), car)

    for coin in coins:
        pygame.draw.rect(screen, (255, 215, 0), coin)

    score_text = font.render(str(score), True, (255, 255, 255))
    screen.blit(score_text, (WIDTH - 50, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()