import pygame
import random

pygame.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

#машина игрока
car = pygame.Rect(180, 500, 40, 60)

#враг
enemy = pygame.Rect(random.randint(0, WIDTH - 40), -60, 40, 60)
enemy_speed = 4

#список монет(словарб)
coins = []
coin_timer = 0

score = 0

#через сколько очков ускоряется враг
level_step = 5

font = pygame.font.SysFont(None, 36)

running = True
while running:
    screen.fill((30, 30, 30))

    #обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #движение игрока
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and car.x > 0:
        car.x -= 5
    if keys[pygame.K_RIGHT] and car.x < WIDTH - car.width:
        car.x += 5

    #движение врага вниз
    enemy.y += enemy_speed

    #если враг вышел за экран
    if enemy.y > HEIGHT:
        enemy.y = -60
        enemy.x = random.randint(0, WIDTH - enemy.width)

    #генерация монет
    coin_timer += 1
    if coin_timer > 40:
        weight = random.choice([1, 2, 3])  #вес монеты
        size = 10 + weight * 5             #размер зависит от веса

        coin = {
            "rect": pygame.Rect(random.randint(0, WIDTH - size), -20, size, size),
            "weight": weight
        }

        coins.append(coin)
        coin_timer = 0

    #обработка монет
    for coin in coins[:]:
        coin["rect"].y += 5

        #если игрок собрал монету
        if coin["rect"].colliderect(car):
            score += coin["weight"]  #добавляем вес
            coins.remove(coin)

        #если монета ушла вниз
        elif coin["rect"].y > HEIGHT:
            coins.remove(coin)

    #ускорение врага каждые level_step очков
    enemy_speed = 4 + (score // level_step)

    #столкновение с врагом
    if car.colliderect(enemy):
        running = False

    #отрисовка игрока
    pygame.draw.rect(screen, (0, 0, 255), car)

    #отрисовка врага
    pygame.draw.rect(screen, (255, 0, 0), enemy)

    #отрисовка монет
    for coin in coins:
        if coin["weight"] == 1:
            color = (200, 200, 0)
        elif coin["weight"] == 2:
            color = (255, 215, 0)
        else:
            color = (255, 255, 100)

        pygame.draw.rect(screen, color, coin["rect"])

    #отображение счёта
    score_text = font.render("Score: " + str(score), True, (255, 255, 255))
    screen.blit(score_text, (WIDTH - 150, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()