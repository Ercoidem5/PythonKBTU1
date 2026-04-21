import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

colors = [
    (0, 0, 0),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 255, 255)
]

current_color = (0, 0, 0)
tool = "brush"

drawing = False
start_pos = (0, 0)

canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill((255, 255, 255))

running = True
while running:
    screen.fill((200, 200, 200))
    screen.blit(canvas, (0, 0))

    for i, color in enumerate(colors):
        pygame.draw.rect(screen, color, (10 + i * 50, 10, 40, 40))

    pygame.draw.rect(screen, (0, 0, 0), (10, 60, 80, 30))
    pygame.draw.rect(screen, (0, 0, 0), (100, 60, 80, 30))
    pygame.draw.rect(screen, (0, 0, 0), (190, 60, 80, 30))
    pygame.draw.rect(screen, (0, 0, 0), (280, 60, 80, 30))

    font = pygame.font.SysFont(None, 24)
    screen.blit(font.render("Brush", True, (255, 255, 255)), (15, 65))
    screen.blit(font.render("Rect", True, (255, 255, 255)), (110, 65))
    screen.blit(font.render("Circle", True, (255, 255, 255)), (195, 65))
    screen.blit(font.render("Eraser", True, (255, 255, 255)), (285, 65))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            for i, color in enumerate(colors):
                if pygame.Rect(10 + i * 50, 10, 40, 40).collidepoint(x, y):
                    current_color = color

            if pygame.Rect(10, 60, 80, 30).collidepoint(x, y):
                tool = "brush"
            if pygame.Rect(100, 60, 80, 30).collidepoint(x, y):
                tool = "rect"
            if pygame.Rect(190, 60, 80, 30).collidepoint(x, y):
                tool = "circle"
            if pygame.Rect(280, 60, 80, 30).collidepoint(x, y):
                tool = "eraser"

            drawing = True
            start_pos = event.pos

        if event.type == pygame.MOUSEBUTTONUP:
            drawing = False
            end_pos = event.pos

            if tool == "rect":
                rect = pygame.Rect(start_pos, (end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]))
                pygame.draw.rect(canvas, current_color, rect, 2)

            if tool == "circle":
                radius = int(((end_pos[0] - start_pos[0]) ** 2 + (end_pos[1] - start_pos[1]) ** 2) ** 0.5)
                pygame.draw.circle(canvas, current_color, start_pos, radius, 2)

        if event.type == pygame.MOUSEMOTION and drawing:
            if tool == "brush":
                pygame.draw.circle(canvas, current_color, event.pos, 5)
            if tool == "eraser":
                pygame.draw.circle(canvas, (255, 255, 255), event.pos, 10)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()