import pygame

class Ball:
    def __init__(self, x, y, radius, screen_width, screen_height):
        self.x = x
        self.y = y
        self.radius = radius
        self.step = 20
        self.screen_width = screen_width
        self.screen_height = screen_height

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy

        if new_x - self.radius >= 0 and new_x + self.radius <= self.screen_width:
            self.x = new_x

        if new_y - self.radius >= 0 and new_y + self.radius <= self.screen_height:
            self.y = new_y

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), (self.x, self.y), self.radius)