import pygame
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

#список доступных цветов
colors = [
    (0, 0, 0),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 255, 255)
]

current_color = (0, 0, 0)  #текущий выбранный цвет
tool = "brush"             #текущий инструмент

drawing = False            #флаг рисования
start_pos = (0, 0)         #начальная точка фигуры

#поверхность для рисования
canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill((255, 255, 255))

#функция для нормализации прямоугольника
def normalize_rect(start, end):
    x1, y1 = start
    x2, y2 = end
    x = min(x1, x2)
    y = min(y1, y2)
    w = abs(x1 - x2)
    h = abs(y1 - y2)
    return pygame.Rect(x, y, w, h)

running = True
while running:
    #очистка экрана и отображение холста
    screen.fill((200, 200, 200))
    screen.blit(canvas, (0, 0))

    #отрисовка палитры цветов
    for i, color in enumerate(colors):
        pygame.draw.rect(screen, color, (10 + i * 50, 10, 40, 40))

    #список инструментов
    buttons = ["Brush", "Rect", "Circle", "Eraser", "Square", "R-Tri", "E-Tri", "Rhombus"]

    #отрисовка кнопок инструментов
    for i, name in enumerate(buttons):
        pygame.draw.rect(screen, (0, 0, 0), (10 + i * 90, 60, 80, 30))
        font = pygame.font.SysFont(None, 20)
        screen.blit(font.render(name, True, (255, 255, 255)), (15 + i * 90, 65))

    for event in pygame.event.get():
        #выход из программы
        if event.type == pygame.QUIT:
            running = False

        #нажатие кнопки мыши
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            #выбор цвета
            for i, color in enumerate(colors):
                if pygame.Rect(10 + i * 50, 10, 40, 40).collidepoint(x, y):
                    current_color = color

            #выбор инструмента
            for i, name in enumerate(buttons):
                if pygame.Rect(10 + i * 90, 60, 80, 30).collidepoint(x, y):
                    tool = name.lower()

            drawing = True
            start_pos = event.pos

        #отпускание кнопки мыши - завершение рисования фигуры
        if event.type == pygame.MOUSEBUTTONUP:
            drawing = False
            end_pos = event.pos

            rect = normalize_rect(start_pos, end_pos)
            
            #прямоугольник
            if tool == "rect":
                pygame.draw.rect(canvas, current_color, rect, 2)

            #квадрат
            if tool == "square":
                size = min(rect.w, rect.h)
                pygame.draw.rect(canvas, current_color, (rect.x, rect.y, size, size), 2)

            #круг
            if tool == "circle":
                radius = int(math.hypot(end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]))
                pygame.draw.circle(canvas, current_color, start_pos, radius, 2)

            #прямоугольный треугольник
            if tool == "r-tri":
                points = [start_pos, (start_pos[0], end_pos[1]), end_pos]
                pygame.draw.polygon(canvas, current_color, points, 2)

            #равносторонний треугольник
            if tool == "e-tri":
                side = rect.w
                h = int(side * math.sqrt(3) / 2)
                p1 = (rect.x, rect.y + h)
                p2 = (rect.x + side // 2, rect.y)
                p3 = (rect.x + side, rect.y + h)
                pygame.draw.polygon(canvas, current_color, [p1, p2, p3], 2)

            #ромб
            if tool == "rhombus":
                cx = rect.x + rect.w // 2
                cy = rect.y + rect.h // 2
                points = [
                    (cx, rect.y),
                    (rect.x + rect.w, cy),
                    (cx, rect.y + rect.h),
                    (rect.x, cy)
                ]
                pygame.draw.polygon(canvas, current_color, points, 2)

        #движение мыши при зажатой кнопке - рисование кистью или ластиком
        if event.type == pygame.MOUSEMOTION and drawing:
            if tool == "brush":
                pygame.draw.circle(canvas, current_color, event.pos, 5)
            if tool == "eraser":
                pygame.draw.circle(canvas, (255, 255, 255), event.pos, 10)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()