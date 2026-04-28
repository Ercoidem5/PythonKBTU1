import pygame
import math
from collections import deque
from datetime import datetime

pygame.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS 2 Paint")
clock = pygame.time.Clock()

# settings 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

colors = [
    BLACK,
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    WHITE
]

brush_sizes = {
    1: 2,
    2: 5,
    3: 10
}

brush_size = 2
current_color = BLACK
tool = "pencil"

canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill(WHITE)

drawing = False
start_pos = (0, 0)
last_pos = (0, 0)

# text tool
text_mode = False
text_pos = (0, 0)
text_input = ""
font = pygame.font.SysFont(None, 28)

# helpers 
def normalize_rect(start, end):
    x1, y1 = start
    x2, y2 = end
    return pygame.Rect(
        min(x1, x2),
        min(y1, y2),
        abs(x1 - x2),
        abs(y1 - y2)
    )

def flood_fill(surface, x, y, new_color):
    target = surface.get_at((x, y))[:3]

    if target == new_color:
        return

    q = deque()
    q.append((x, y))

    while q:
        px, py = q.popleft()

        if px < 0 or px >= WIDTH or py < 0 or py >= HEIGHT:
            continue

        if surface.get_at((px, py))[:3] != target:
            continue

        surface.set_at((px, py), new_color)

        q.append((px + 1, py))
        q.append((px - 1, py))
        q.append((px, py + 1))
        q.append((px, py - 1))

def save_canvas():
    filename = datetime.now().strftime("paint_%Y%m%d_%H%M%S.png")
    pygame.image.save(canvas, filename)
    print("Saved:", filename)

def draw_preview(surface):
    if not drawing:
        return

    mx, my = pygame.mouse.get_pos()
    rect = normalize_rect(start_pos, (mx, my))

    if tool == "line":
        pygame.draw.line(surface, current_color, start_pos, (mx, my), brush_size)

    elif tool == "rect":
        pygame.draw.rect(surface, current_color, rect, brush_size)

    elif tool == "square":
        size = min(rect.w, rect.h)
        pygame.draw.rect(surface, current_color,
                         (rect.x, rect.y, size, size), brush_size)

    elif tool == "circle":
        radius = int(math.hypot(mx - start_pos[0], my - start_pos[1]))
        pygame.draw.circle(surface, current_color, start_pos, radius, brush_size)

    elif tool == "r-tri":
        pts = [start_pos, (start_pos[0], my), (mx, my)]
        pygame.draw.polygon(surface, current_color, pts, brush_size)

    elif tool == "e-tri":
        side = rect.w
        h = int(side * math.sqrt(3) / 2)
        pts = [
            (rect.x, rect.y + h),
            (rect.x + side // 2, rect.y),
            (rect.x + side, rect.y + h)
        ]
        pygame.draw.polygon(surface, current_color, pts, brush_size)

    elif tool == "rhombus":
        cx = rect.x + rect.w // 2
        cy = rect.y + rect.h // 2
        pts = [
            (cx, rect.y),
            (rect.x + rect.w, cy),
            (cx, rect.y + rect.h),
            (rect.x, cy)
        ]
        pygame.draw.polygon(surface, current_color, pts, brush_size)

# UI 
buttons = [
    "Pencil", "Line", "Rect", "Circle", "Eraser",
    "Square", "R-Tri", "E-Tri", "Rhombus",
    "Fill", "Text"
]

running = True
while running:
    screen.fill(GRAY)
    screen.blit(canvas, (0, 0))

    # palette
    for i, color in enumerate(colors):
        pygame.draw.rect(screen, color, (10 + i * 50, 10, 40, 40))
        pygame.draw.rect(screen, BLACK, (10 + i * 50, 10, 40, 40), 1)

    # tool buttons
    for i, name in enumerate(buttons):
        pygame.draw.rect(screen, BLACK, (10 + i * 90, 60, 80, 30))
        txt = font.render(name, True, WHITE)
        screen.blit(txt, (15 + i * 90, 67))

    # brush size text
    size_text = font.render(f"Size: {brush_size}px (1/2/3)", True, BLACK)
    screen.blit(size_text, (10, 105))

    # preview
    preview = screen.copy()
    draw_preview(preview)
    screen.blit(preview, (0, 0))

    # text preview
    if text_mode:
        txt = font.render(text_input, True, current_color)
        screen.blit(txt, text_pos)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # keyboard
        if event.type == pygame.KEYDOWN:

            # save
            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                save_canvas()

            # brush sizes
            elif event.key == pygame.K_1:
                brush_size = brush_sizes[1]
            elif event.key == pygame.K_2:
                brush_size = brush_sizes[2]
            elif event.key == pygame.K_3:
                brush_size = brush_sizes[3]

            # text typing
            if text_mode:
                if event.key == pygame.K_RETURN:
                    txt = font.render(text_input, True, current_color)
                    canvas.blit(txt, text_pos)
                    text_mode = False
                    text_input = ""

                elif event.key == pygame.K_ESCAPE:
                    text_mode = False
                    text_input = ""

                elif event.key == pygame.K_BACKSPACE:
                    text_input = text_input[:-1]

                else:
                    text_input += event.unicode

        # mouse down
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            # choose color
            for i, color in enumerate(colors):
                if pygame.Rect(10 + i * 50, 10, 40, 40).collidepoint(x, y):
                    current_color = color

            # choose tool
            for i, name in enumerate(buttons):
                if pygame.Rect(10 + i * 90, 60, 80, 30).collidepoint(x, y):
                    tool = name.lower()

            # text tool
            if tool == "text":
                text_mode = True
                text_input = ""
                text_pos = event.pos

            # fill tool
            elif tool == "fill":
                flood_fill(canvas, x, y, current_color)

            else:
                drawing = True
                start_pos = event.pos
                last_pos = event.pos

        # mouse move
        if event.type == pygame.MOUSEMOTION and drawing:

            if tool == "pencil":
                pygame.draw.line(canvas, current_color,
                                 last_pos, event.pos, brush_size)
                last_pos = event.pos

            elif tool == "eraser":
                pygame.draw.line(canvas, WHITE,
                                 last_pos, event.pos, brush_size * 2)
                last_pos = event.pos

        # mouse up
        if event.type == pygame.MOUSEBUTTONUP and drawing:
            drawing = False
            end_pos = event.pos
            rect = normalize_rect(start_pos, end_pos)

            if tool == "line":
                pygame.draw.line(canvas, current_color,
                                 start_pos, end_pos, brush_size)

            elif tool == "rect":
                pygame.draw.rect(canvas, current_color, rect, brush_size)

            elif tool == "square":
                size = min(rect.w, rect.h)
                pygame.draw.rect(canvas, current_color,
                                 (rect.x, rect.y, size, size), brush_size)

            elif tool == "circle":
                radius = int(math.hypot(
                    end_pos[0] - start_pos[0],
                    end_pos[1] - start_pos[1]
                ))
                pygame.draw.circle(canvas, current_color,
                                   start_pos, radius, brush_size)

            elif tool == "r-tri":
                pts = [start_pos, (start_pos[0], end_pos[1]), end_pos]
                pygame.draw.polygon(canvas, current_color, pts, brush_size)

            elif tool == "e-tri":
                side = rect.w
                h = int(side * math.sqrt(3) / 2)
                pts = [
                    (rect.x, rect.y + h),
                    (rect.x + side // 2, rect.y),
                    (rect.x + side, rect.y + h)
                ]
                pygame.draw.polygon(canvas, current_color, pts, brush_size)

            elif tool == "rhombus":
                cx = rect.x + rect.w // 2
                cy = rect.y + rect.h // 2
                pts = [
                    (cx, rect.y),
                    (rect.x + rect.w, cy),
                    (cx, rect.y + rect.h),
                    (rect.x, cy)
                ]
                pygame.draw.polygon(canvas, current_color, pts, brush_size)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()