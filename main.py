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
        self.base_width = PADDLE_WIDTH
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
        color = COLOR_PADDLE
        rx, ry = self.x + offset[0], self.y + offset[1]

        aura = pygame.Surface((self.width + 12, self.height + 12), pygame.SRCALPHA)
        pygame.draw.rect(aura, (*color, 65), aura.get_rect(), border_radius=10)
        surface.blit(aura, (rx - 6, ry - 6))

        pygame.draw.rect(surface, color, (rx, ry, self.width, self.height), border_radius=7)
        pygame.draw.rect(surface, (245, 240, 255), (rx + 6, ry + 3, self.width - 12, 3), border_radius=2)

class Ball:
    def __init__(self, x=None, y=None):
        self.radius = BALL_RADIUS
        self.x = x if x else SCREEN_WIDTH // 2
        self.y = y if y else SCREEN_HEIGHT - 80
        angle = math.radians(random.choice([-55, -35, 35, 55]))
        self.vx = BALL_BASE_SPEED * math.sin(angle)
        self.vy = -BALL_BASE_SPEED * math.cos(angle)
        self.trail = []

    @property
    def rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 9:
            self.trail.pop(0)

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
        glow_c = COLOR_BALL_GLOW
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(65 * (i + 1) / len(self.trail))
            r_size = int(self.radius * (0.5 + 0.5 * (i / len(self.trail))))
            t_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(t_surf, (*glow_c, alpha), (self.radius, self.radius), r_size)
            surface.blit(t_surf, (tx - self.radius + offset[0], ty - self.radius + offset[1]))

        pygame.draw.circle(surface, COLOR_BALL, (int(self.x + offset[0]), int(self.y + offset[1])), self.radius)

class Brick:
    def __init__(self, x, y, width, height, tier):
        self.rect = pygame.Rect(x, y, width, height)
        self.tier = tier
        self.hp = tier
        self.base_color = BRICK_TYPES[tier]["color"]
        self.points = BRICK_TYPES[tier]["points"]

    def hit(self, damage=1):
        self.hp -= damage
        return self.hp <= 0

    def draw(self, surface, offset=(0, 0)):
        alpha = int(120 + (135 * (self.hp / self.tier)))
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (*self.base_color, alpha), (0, 0, self.rect.width, self.rect.height), border_radius=5)
        pygame.draw.rect(s, (255, 255, 255, 130), (0, 0, self.rect.width, self.rect.height), width=1, border_radius=5)
        surface.blit(s, (self.rect.x + offset[0], self.rect.y + offset[1]))

def create_cyber_matrix():
    bricks = []
    rows, cols = 6, 10
    pad_x, pad_y = 10, 10
    brick_w = (SCREEN_WIDTH - 60 - ((cols - 1) * pad_x)) // cols
    brick_h = 24
    for r in range(rows):
        tier = 4 if r == 0 else (3 if r == 1 else (2 if r in [2, 3] else 1))
        for c in range(cols):
            bx = 30 + c * (brick_w + pad_x)
            by = 90 + r * (brick_h + pad_y)
            bricks.append(Brick(bx, by, brick_w, brick_h, tier))
    return bricks

def draw_cyber_grid(surface, offset=(0, 0)):
    for x in range(0, SCREEN_WIDTH, 40):
        pygame.draw.line(surface, COLOR_GRID, (x + offset[0] // 2, 60), (x + offset[0] // 2, SCREEN_HEIGHT))
    for y in range(60, SCREEN_HEIGHT, 40):
        pygame.draw.line(surface, COLOR_GRID, (0, y + offset[1] // 2), (SCREEN_WIDTH, y + offset[1] // 2))

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("NekoBreaker: Angled Deflection")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Consolas", 18, bold=True)

    paddle = Paddle()
    ball = Ball()
    bricks = create_cyber_matrix()
    score, lives, combo = 0, 3, 0

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
            offset_hit = (ball.x - paddle.rect.centerx) / (paddle.width / 2)
            ball.vx = offset_hit * 8.0
            ball.vy = -abs(ball.vy)
            combo = 0

        for brick in bricks[:]:
            if ball.rect.colliderect(brick.rect):
                prev_x = ball.x - ball.vx
                if prev_x + ball.radius <= brick.rect.left or prev_x - ball.radius >= brick.rect.right:
                    ball.vx *= -1
                else:
                    ball.vy *= -1

                combo += 1
                if brick.hit(1):
                    score += brick.points * combo
                    bricks.remove(brick)
                break

        if ball.y > SCREEN_HEIGHT:
            lives -= 1
            combo = 0
            if lives <= 0:
                ball = Ball()
                score, lives = 0, 3
                bricks = create_cyber_matrix()
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
        screen.blit(font.render(f"COMBO: x{combo}", True, (0, 255, 220) if combo > 1 else (110, 100, 150)), (210, 20))
        screen.blit(font.render(f"LIVES: {lives}", True, COLOR_TEXT), (SCREEN_WIDTH - 140, 20))

        pygame.display.flip()

if __name__ == "__main__":
    main()
