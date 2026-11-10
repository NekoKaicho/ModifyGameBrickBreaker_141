import pygame
import sys
import math
import random
import io
import wave
import struct

SCREEN_WIDTH = 850
SCREEN_HEIGHT = 680
FPS = 60

COLOR_BG = (8, 6, 18)
COLOR_GRID = (24, 18, 52)
COLOR_PADDLE = (165, 95, 255)
COLOR_PADDLE_EXPAND = (60, 235, 255)
COLOR_BALL = (245, 250, 255)
COLOR_BALL_GLOW = (150, 60, 245)
COLOR_LASER = (0, 255, 230)
COLOR_TEXT = (235, 230, 255)
COLOR_MUTED = (125, 115, 155)
COLOR_ACCENT = (0, 255, 220)
COLOR_GOLD = (255, 215, 60)
COLOR_RED = (255, 65, 115)

BRICK_TYPES = {
    1: {"color": (120, 80, 255),  "points": 15, "name": "Cyber-I"},
    2: {"color": (0, 210, 255),   "points": 35, "name": "Cyber-II"},
    3: {"color": (230, 50, 210),  "points": 60, "name": "Pulse Core"},
    4: {"color": (255, 215, 60),  "points": 100, "name": "Hyper Reactor"},
}

POWERUP_TYPES = {
    "EXPAND": {"color": (0, 255, 180), "label": "WIDE"},
    "LASER":  {"color": (255, 60, 160), "label": "GUN"},
    "MULTI":  {"color": (255, 210, 0),  "label": "x2"},
    "HEAL":   {"color": (255, 65, 115), "label": "+1"},
}

PADDLE_WIDTH = 115
PADDLE_HEIGHT = 16
PADDLE_SPEED = 9.5
BALL_RADIUS = 8
BALL_BASE_SPEED = 7.2

class Paddle:
    def __init__(self):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = SCREEN_HEIGHT - 48
        self.speed = PADDLE_SPEED

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, dx):
        self.x = max(12, min(SCREEN_WIDTH - self.width - 12, self.x + dx * self.speed))

    def update(self):
        pass

    def draw(self, surface, offset=(0, 0)):
        rx, ry = self.x + offset[0], self.y + offset[1]
        pygame.draw.rect(surface, COLOR_PADDLE, (rx, ry, self.width, self.height), border_radius=6)

class Ball:
    def __init__(self, x=None, y=None):
        self.radius = BALL_RADIUS
        self.x = x if x else SCREEN_WIDTH // 2
        self.y = y if y else SCREEN_HEIGHT - 80
        angle = math.radians(random.choice([-45, 45]))
        self.vx = BALL_BASE_SPEED * math.sin(angle)
        self.vy = -BALL_BASE_SPEED * math.cos(angle)

    @property
    def rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def update(self):
        self.x += self.vx
        self.y += self.vy

        if self.x - self.radius <= 0:
            self.x = self.radius
            self.vx *= -1
        elif self.x + self.radius >= SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.radius
            self.vx *= -1

        if self.y - self.radius <= 60:
            self.y = 60 + self.radius
            self.vy *= -1

    def draw(self, surface, offset=(0, 0)):
        pygame.draw.circle(surface, COLOR_BALL, (int(self.x + offset[0]), int(self.y + offset[1])), self.radius)

class Brick:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.points = 20

    def draw(self, surface, offset=(0, 0)):
        pygame.draw.rect(surface, (120, 80, 255), self.rect.move(offset), border_radius=4)

def create_bricks():
    bricks = []
    rows, cols = 5, 10
    pad_x, pad_y = 10, 10
    brick_w = (SCREEN_WIDTH - 60 - ((cols - 1) * pad_x)) // cols
    brick_h = 24
    for r in range(rows):
        for c in range(cols):
            bx = 30 + c * (brick_w + pad_x)
            by = 90 + r * (brick_h + pad_y)
            bricks.append(Brick(bx, by, brick_w, brick_h))
    return bricks

def draw_cyber_grid(surface, offset=(0, 0)):
    for x in range(0, SCREEN_WIDTH, 40):
        pygame.draw.line(surface, COLOR_GRID, (x + offset[0] // 2, 60), (x + offset[0] // 2, SCREEN_HEIGHT))
    for y in range(60, SCREEN_HEIGHT, 40):
        pygame.draw.line(surface, COLOR_GRID, (0, y + offset[1] // 2), (SCREEN_WIDTH, y + offset[1] // 2))

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("NekoBreaker: Cyber Theme")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Consolas", 18, bold=True)

    paddle = Paddle()
    ball = Ball()
    bricks = create_bricks()
    score, lives = 0, 3

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        paddle.move(dx)
        paddle.update()

        ball.update()

        if ball.rect.colliderect(paddle.rect) and ball.vy > 0:
            ball.vy *= -1

        for brick in bricks[:]:
            if ball.rect.colliderect(brick.rect):
                ball.vy *= -1
                score += brick.points
                bricks.remove(brick)
                break

        if ball.y > SCREEN_HEIGHT:
            lives -= 1
            if lives <= 0:
                ball = Ball()
                score, lives = 0, 3
                bricks = create_bricks()
            else:
                ball = Ball()

        screen.fill(COLOR_BG)
        draw_cyber_grid(screen)

        for b in bricks:
            b.draw(screen)
        paddle.draw(screen)
        ball.draw(screen)

        pygame.draw.rect(screen, (14, 10, 30), (0, 0, SCREEN_WIDTH, 60))
        pygame.draw.line(screen, COLOR_PADDLE, (0, 60), (SCREEN_WIDTH, 60), 2)
        screen.blit(font.render(f"SCORE: {score}", True, COLOR_TEXT), (20, 20))
        screen.blit(font.render(f"LIVES: {lives}", True, COLOR_TEXT), (SCREEN_WIDTH - 140, 20))

        pygame.display.flip()

if __name__ == "__main__":
    main()
