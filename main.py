import pygame
import sys

SCREEN_WIDTH = 850
SCREEN_HEIGHT = 680
FPS = 60

COLOR_BG = (15, 15, 25)
COLOR_WHITE = (255, 255, 255)
COLOR_PADDLE = (160, 100, 240)
COLOR_BALL = (255, 255, 255)
COLOR_BRICK = (100, 130, 220)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("NekoBreaker - Base Arcade")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Consolas", 20, bold=True)

    paddle_w, paddle_h = 110, 15
    paddle_x = (SCREEN_WIDTH - paddle_w) // 2
    paddle_y = SCREEN_HEIGHT - 50
    paddle_speed = 8

    ball_r = 8
    ball_x, ball_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80
    ball_vx, ball_vy = 5, -5

    rows, cols = 5, 10
    brick_w = (SCREEN_WIDTH - 60 - ((cols - 1) * 10)) // cols
    brick_h = 22
    bricks = []
    for r in range(rows):
        for c in range(cols):
            bx = 30 + c * (brick_w + 10)
            by = 80 + r * (brick_h + 10)
            bricks.append(pygame.Rect(bx, by, brick_w, brick_h))

    score = 0
    lives = 3

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and paddle_x > 10:
            paddle_x -= paddle_speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and paddle_x < SCREEN_WIDTH - paddle_w - 10:
            paddle_x += paddle_speed

        ball_x += ball_vx
        ball_y += ball_vy

        if ball_x - ball_r <= 0 or ball_x + ball_r >= SCREEN_WIDTH:
            ball_vx *= -1
        if ball_y - ball_r <= 60:
            ball_vy *= -1

        paddle_rect = pygame.Rect(paddle_x, paddle_y, paddle_w, paddle_h)
        ball_rect = pygame.Rect(ball_x - ball_r, ball_y - ball_r, ball_r * 2, ball_r * 2)
        if ball_rect.colliderect(paddle_rect) and ball_vy > 0:
            ball_vy *= -1

        for b in bricks[:]:
            if ball_rect.colliderect(b):
                ball_vy *= -1
                bricks.remove(b)
                score += 10
                break

        if ball_y > SCREEN_HEIGHT:
            lives -= 1
            if lives <= 0:
                ball_x, ball_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80
                ball_vx, ball_vy = 0, 0
            else:
                ball_x, ball_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80
                ball_vx, ball_vy = 5, -5

        screen.fill(COLOR_BG)
        pygame.draw.line(screen, (70, 70, 100), (0, 60), (SCREEN_WIDTH, 60), 2)
        pygame.draw.rect(screen, COLOR_PADDLE, paddle_rect, border_radius=4)
        pygame.draw.circle(screen, COLOR_BALL, (int(ball_x), int(ball_y)), ball_r)

        for b in bricks:
            pygame.draw.rect(screen, COLOR_BRICK, b, border_radius=4)

        score_text = font.render(f"SCORE: {score}   LIVES: {lives}", True, COLOR_WHITE)
        screen.blit(score_text, (20, 20))
        pygame.display.flip()

if __name__ == "__main__":
    main()
