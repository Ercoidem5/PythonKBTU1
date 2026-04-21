import pygame
import time
import math

def draw_line(surface, angle, length, color, width, center):
    angle_rad = math.radians(angle - 90)
    x = center[0] + length * math.cos(angle_rad)
    y = center[1] + length * math.sin(angle_rad)
    pygame.draw.line(surface, color, center, (x, y), width)

def draw_clock(surface, width, height):
    now = time.localtime()
    hours = now.tm_hour % 12
    minutes = now.tm_min
    seconds = now.tm_sec

    center = (width // 2, height // 2)

    second_angle = seconds * 6
    minute_angle = minutes * 6 + seconds * 0.1
    hour_angle = hours * 30 + minutes * 0.5

    draw_line(surface, hour_angle, 120, (0, 0, 0), 8, center)
    draw_line(surface, minute_angle, 180, (0, 0, 0), 5, center)
    draw_line(surface, second_angle, 200, (255, 0, 0), 2, center)