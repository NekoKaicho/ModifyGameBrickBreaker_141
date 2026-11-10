import pygame
import sys
import math
import random

SCREEN_WIDTH = 850
SCREEN_HEIGHT = 680
FPS = 60

COLOR_BG = (15, 15, 25)
COLOR_TEXT = (240, 240, 255)
COLOR_PADDLE = (160, 100, 240)
COLOR_BALL = (255, 255, 255)
COLOR_BRICK = (100, 130, 220)

PADDLE_WIDTH = 115
PADDLE_HEIGHT = 16
PADDLE_SPEED = 9.5
BALL_RADIUS = 8
BALL_SPEED = 7.2

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
        self.vx = BALL_SPEED * math.sin(angle)
        self.vy = -BALL_SPEED * math.cos(angle)

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
        pygame.draw.rect(surface, COLOR_BRICK, self.rect.move(offset), border_radius=4)

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

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("NekoBreaker: OOP Architecture")
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
