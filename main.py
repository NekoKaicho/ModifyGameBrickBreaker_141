"""
================================================================================
                    NEKOBREAKER: CYBER OVERDRIVE
                   Dikembangkan oleh: Heyden Alyas
================================================================================
Arsitektur game arcade Brick Breaker bertema Cyberpunk berkecepatan tinggi,
dilengkapi partikel plasma, getaran layar, audio prosedural, sistem power-up,
meriam laser, mode Overdrive penembus matrix, serta menu pause dan navigasi lengkap.
"""

import pygame
import sys
import math
import random
import io
import wave
import struct

# ==============================================================================
# 1. KONFIGURASI LAYAR & PALET WARNA CYBER-ARCADE
# ==============================================================================
SCREEN_WIDTH = 850
SCREEN_HEIGHT = 680
FPS = 60

COLOR_BG = (8, 6, 18)                # Deep Void Space
COLOR_GRID = (24, 18, 52)            # Ultraviolet Cyber Grid
COLOR_PADDLE = (165, 95, 255)        # Electric Violet Core
COLOR_PADDLE_EXPAND = (60, 235, 255) # Plasma Cyan
COLOR_BALL = (245, 250, 255)         # White-Hot Fusion Core
COLOR_BALL_GLOW = (150, 60, 245)     # Neon Violet Glow
COLOR_LASER = (0, 255, 230)          # Cyber Ion Beam
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

# ==============================================================================
# 2. AUDIO SYNTHESIZER (8-BIT PROCEDURAL SOUND EFFECTS)
# ==============================================================================
class SoundManager:
    """Menghasilkan efek suara retro sci-fi prosedural tanpa dependensi file audio luar."""
    def __init__(self):
        self.enabled = True
        self.sounds = {}
        try:
            pygame.mixer.init(22050, -16, 1, 512)
            self.sounds["paddle"] = self._create_tone(480, 0.05, 0.22, decay=True)
            self.sounds["brick"] = self._create_tone(360, 0.07, 0.25, decay=True)
            self.sounds["laser"] = self._create_laser_tone()
            self.sounds["powerup"] = self._create_powerup_tone()
            self.sounds["overdrive"] = self._create_tone(180, 0.35, 0.40, decay=False)
            self.sounds["gameover"] = self._create_descending_tone()
            self.sounds["victory"] = self._create_victory_tone()
        except Exception:
            self.enabled = False

    def _create_tone(self, freq, duration, volume=0.3, decay=True):
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            frames = bytearray()
            for i in range(n_samples):
                t = float(i) / sample_rate
                env = (1.0 - float(i) / n_samples) if decay else 1.0
                val = int(volume * 32767.0 * math.sin(2.0 * math.pi * freq * t) * env)
                frames.extend(struct.pack('<h', max(-32767, min(32767, val))))
            wav.writeframes(frames)
        buf.seek(0)
        return pygame.mixer.Sound(buf)

    def _create_laser_tone(self):
        sample_rate = 22050
        duration = 0.11
        n_samples = int(sample_rate * duration)
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            frames = bytearray()
            for i in range(n_samples):
                p = float(i) / n_samples
                freq = 880.0 - (p * 500.0)
                t = float(i) / sample_rate
                val = int(0.24 * 32767.0 * math.sin(2.0 * math.pi * freq * t) * (1.0 - p))
                frames.extend(struct.pack('<h', max(-32767, min(32767, val))))
            wav.writeframes(frames)
        buf.seek(0)
        return pygame.mixer.Sound(buf)

    def _create_powerup_tone(self):
        sample_rate = 22050
        duration = 0.16
        n_samples = int(sample_rate * duration)
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            frames = bytearray()
            for i in range(n_samples):
                p = float(i) / n_samples
                freq = 420.0 + (p * 480.0)
                t = float(i) / sample_rate
                val = int(0.28 * 32767.0 * math.sin(2.0 * math.pi * freq * t) * (1.0 - p * 0.4))
                frames.extend(struct.pack('<h', max(-32767, min(32767, val))))
            wav.writeframes(frames)
        buf.seek(0)
        return pygame.mixer.Sound(buf)

    def _create_descending_tone(self):
        sample_rate = 22050
        duration = 0.38
        n_samples = int(sample_rate * duration)
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            frames = bytearray()
            for i in range(n_samples):
                p = float(i) / n_samples
                freq = max(55.0, 360.0 - (p * 280.0))
                t = float(i) / sample_rate
                val = int(0.3 * 32767.0 * math.sin(2.0 * math.pi * freq * t) * (1.0 - p))
                frames.extend(struct.pack('<h', max(-32767, min(32767, val))))
            wav.writeframes(frames)
        buf.seek(0)
        return pygame.mixer.Sound(buf)

    def _create_victory_tone(self):
        sample_rate = 22050
        duration = 0.35
        n_samples = int(sample_rate * duration)
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            frames = bytearray()
            for i in range(n_samples):
                p = float(i) / n_samples
                freq = 320.0 + (math.sin(p * math.pi * 4) * 110.0) + (p * 290.0)
                t = float(i) / sample_rate
                val = int(0.3 * 32767.0 * math.sin(2.0 * math.pi * freq * t) * (1.0 - p * 0.3))
                frames.extend(struct.pack('<h', max(-32767, min(32767, val))))
            wav.writeframes(frames)
        buf.seek(0)
        return pygame.mixer.Sound(buf)

    def play(self, name):
        if self.enabled and name in self.sounds:
            try:
                self.sounds[name].play()
            except Exception:
                pass

    def toggle(self):
        self.enabled = not self.enabled
        return self.enabled

# ==============================================================================
# 3. SISTEM EFEK VISUAL (VFX, PARTIKEL & SCREEN SHAKE)
# ==============================================================================
class ScreenShake:
    def __init__(self):
        self.timer = 0
        self.magnitude = 0

    def trigger(self, frames=8, magnitude=5):
        self.timer = frames
        self.magnitude = magnitude

    def get_offset(self):
        if self.timer > 0:
            self.timer -= 1
            return (random.randint(-self.magnitude, self.magnitude),
                    random.randint(-self.magnitude, self.magnitude))
        return (0, 0)

class Shockwave:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 5
        self.max_radius = 55
        self.alpha = 220

    def update(self):
        self.radius += 3.5
        self.alpha = max(0, self.alpha - 14)

    def draw(self, surface, offset=(0, 0)):
        if self.alpha > 0 and self.radius >= 2:
            size = int(self.radius * 2)
            s = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, int(self.alpha)), (int(self.radius), int(self.radius)), int(self.radius), width=2)
            surface.blit(s, (self.x - self.radius + offset[0], self.y - self.radius + offset[1]))

class PlasmaParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.uniform(3, 6.5)
        self.vx = random.uniform(-4.5, 4.5)
        self.vy = random.uniform(-4.5, 4.5)
        self.alpha = 255
        self.decay = random.uniform(7, 13)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.alpha -= self.decay
        self.size = max(0, self.size - 0.12)

    def draw(self, surface, offset=(0, 0)):
        if self.alpha > 0 and self.size >= 1:
            size_int = max(2, int(self.size * 2))
            rad = max(1, int(self.size))
            s = pygame.Surface((size_int, size_int), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, max(0, min(255, int(self.alpha)))), (rad, rad), rad)
            surface.blit(s, (self.x - self.size + offset[0], self.y - self.size + offset[1]))

class VFXManager:
    def __init__(self):
        self.particles = []
        self.shockwaves = []
        self.shaker = ScreenShake()

    def spawn_burst(self, x, y, color, count=16, ring=False):
        for _ in range(count):
            self.particles.append(PlasmaParticle(x, y, color))
        if ring:
            self.shockwaves.append(Shockwave(x, y, color))

    def update_and_draw(self, surface):
        offset = self.shaker.get_offset()
        for p in self.particles[:]:
            p.update()
            if p.alpha <= 0 or p.size <= 0:
                self.particles.remove(p)
            else:
                p.draw(surface, offset)

        for sw in self.shockwaves[:]:
            sw.update()
            if sw.alpha <= 0:
                self.shockwaves.remove(sw)
            else:
                sw.draw(surface, offset)
        return offset

# ==============================================================================
# 4. KELAS ENTITAS GAME
# ==============================================================================
class LaserBolt:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 2, y, 4, 16)
        self.vy = -12

    def update(self):
        self.rect.y += self.vy

    def draw(self, surface, offset=(0, 0)):
        r = self.rect.move(offset)
        pygame.draw.rect(surface, COLOR_LASER, r, border_radius=2)

class PowerUpCapsule:
    def __init__(self, x, y, p_type):
        self.rect = pygame.Rect(x - 18, y - 9, 36, 18)
        self.p_type = p_type
        self.color = POWERUP_TYPES[p_type]["color"]
        self.label = POWERUP_TYPES[p_type]["label"]
        self.vy = 3.2

    def update(self):
        self.rect.y += self.vy

    def draw(self, surface, font, offset=(0, 0)):
        r = self.rect.move(offset)
        pygame.draw.rect(surface, self.color, r, border_radius=9)
        pygame.draw.rect(surface, (255, 255, 255), r, width=1, border_radius=9)
        txt = font.render(self.label, True, (10, 10, 20))
        surface.blit(txt, (r.centerx - txt.get_width() // 2, r.centery - txt.get_height() // 2))

class Paddle:
    def __init__(self):
        self.base_width = PADDLE_WIDTH
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = SCREEN_HEIGHT - 48
        self.speed = PADDLE_SPEED
        self.expand_timer = 0
        self.laser_timer = 0
        self.laser_cooldown = 0

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        if self.expand_timer > 0:
            self.expand_timer -= 1
            self.width = int(self.base_width * 1.45)
        else:
            self.width = self.base_width

        if self.laser_timer > 0:
            self.laser_timer -= 1
        if self.laser_cooldown > 0:
            self.laser_cooldown -= 1

    def move(self, dx):
        self.x = max(12, min(SCREEN_WIDTH - self.width - 12, self.x + dx * self.speed))

    def can_shoot(self):
        return self.laser_timer > 0 and self.laser_cooldown == 0

    def shoot(self):
        self.laser_cooldown = 18
        return [LaserBolt(self.x + 10, self.y), LaserBolt(self.x + self.width - 10, self.y)]

    def draw(self, surface, offset=(0, 0)):
        color = COLOR_PADDLE_EXPAND if self.expand_timer > 0 else COLOR_PADDLE
        rx, ry = self.x + offset[0], self.y + offset[1]

        # Outer Cyber Aura
        aura = pygame.Surface((self.width + 12, self.height + 12), pygame.SRCALPHA)
        pygame.draw.rect(aura, (*color, 65), aura.get_rect(), border_radius=10)
        surface.blit(aura, (rx - 6, ry - 6))

        # Core Paddle
        pygame.draw.rect(surface, color, (rx, ry, self.width, self.height), border_radius=7)
        pygame.draw.rect(surface, (245, 240, 255), (rx + 6, ry + 3, self.width - 12, 3), border_radius=2)

        # Dual Laser Turret Nodes
        if self.laser_timer > 0:
            pygame.draw.circle(surface, COLOR_LASER, (int(rx + 10), int(ry)), 5)
            pygame.draw.circle(surface, COLOR_LASER, (int(rx + self.width - 10), int(ry)), 5)

class Ball:
    def __init__(self, x=None, y=None, speed=BALL_BASE_SPEED, overdrive=False):
        self.radius = BALL_RADIUS
        self.x = x if x else SCREEN_WIDTH // 2
        self.y = y if y else SCREEN_HEIGHT - 80
        self.speed = speed
        angle = math.radians(random.choice([-55, -35, 35, 55]))
        self.vx = self.speed * math.sin(angle)
        self.vy = -self.speed * math.cos(angle)
        self.trail = []
        self.overdrive = overdrive

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
        glow_c = (0, 255, 230) if self.overdrive else COLOR_BALL_GLOW
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

# ==============================================================================
# 5. GENERATOR MATRIX & BACKGROUND
# ==============================================================================
def create_level_matrix(wave_num=1):
    bricks = []
    rows, cols = 6, 10
    pad_x, pad_y = 10, 10
    brick_w = (SCREEN_WIDTH - 60 - ((cols - 1) * pad_x)) // cols
    brick_h = 24
    for r in range(rows):
        if wave_num == 1:
            tier = 4 if r == 0 else (3 if r == 1 else (2 if r in [2, 3] else 1))
        elif wave_num == 2:
            tier = 4 if r in [0, 1] else (3 if r in [2, 3] else 2)
        else:
            tier = 4 if r in [0, 1, 2] else 3

        for c in range(cols):
            bx = 30 + c * (brick_w + pad_x)
            by = 90 + r * (brick_h + pad_y)
            bricks.append(Brick(bx, by, brick_w, brick_h, tier))
    return bricks

def draw_cyber_grid(surface, offset):
    for x in range(0, SCREEN_WIDTH, 40):
        pygame.draw.line(surface, COLOR_GRID, (x + offset[0] // 2, 60), (x + offset[0] // 2, SCREEN_HEIGHT))
    for y in range(60, SCREEN_HEIGHT, 40):
        pygame.draw.line(surface, COLOR_GRID, (0, y + offset[1] // 2), (SCREEN_WIDTH, y + offset[1] // 2))

# ==============================================================================
# 6. LOOP UTAMA DAN STATE MACHINE GAME
# ==============================================================================
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("NekoBreaker: Cyber Overdrive - by Heyden Alyas")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Consolas", 18, bold=True)
    small_font = pygame.font.SysFont("Consolas", 12, bold=True)
    big_font = pygame.font.SysFont("Consolas", 44, bold=True)
    title_font = pygame.font.SysFont("Consolas", 56, bold=True)

    snd = SoundManager()
    fx = VFXManager()

    high_score = 0
    state = "MENU" # "MENU", "CONTROLS", "PLAYING", "PAUSED", "GAMEOVER", "VICTORY"

    wave_num = 1
    paddle = Paddle()
    balls = [Ball(speed=BALL_BASE_SPEED)]
    bricks = create_level_matrix(wave_num)
    capsules = []
    lasers = []

    score, lives, combo = 0, 3, 0
    max_combo = 0
    cyber_energy = 0 # 0 - 100 Burst Gauge
    overdrive_timer = 0
    title_pulse = 0

    def start_game(reset_all=True):
        nonlocal paddle, balls, bricks, capsules, lasers, score, lives, combo, max_combo, cyber_energy, overdrive_timer, wave_num, state
        if reset_all:
            wave_num = 1
            score = 0
            lives = 3
            combo = 0
            max_combo = 0
            cyber_energy = 0
            overdrive_timer = 0

        current_speed = BALL_BASE_SPEED + (wave_num - 1) * 0.6
        paddle = Paddle()
        balls = [Ball(speed=current_speed)]
        bricks = create_level_matrix(wave_num)
        capsules.clear()
        lasers.clear()
        state = "PLAYING"

    while True:
        clock.tick(FPS)
        title_pulse = (title_pulse + 0.05) % (2 * math.pi)

        # ----------------------------------------------------------------------
        # EVENT HANDLING
        # ----------------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Toggle Mute global
                if event.key == pygame.K_m and state not in ["PAUSED"]:
                    snd.toggle()

                if state == "MENU":
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        start_game(reset_all=True)
                    elif event.key == pygame.K_h:
                        state = "CONTROLS"
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                elif state == "CONTROLS":
                    if event.key in [pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN, pygame.K_h]:
                        state = "MENU"

                elif state == "PLAYING":
                    if event.key in [pygame.K_p, pygame.K_ESCAPE]:
                        state = "PAUSED"
                    elif event.key == pygame.K_LSHIFT and cyber_energy >= 100:
                        overdrive_timer = 360 # 6 Detik Overdrive
                        cyber_energy = 0
                        fx.shaker.trigger(16, 9)
                        snd.play("overdrive")

                elif state == "PAUSED":
                    if event.key in [pygame.K_p, pygame.K_ESCAPE]:
                        state = "PLAYING"
                    elif event.key == pygame.K_r:
                        start_game(reset_all=False)
                    elif event.key == pygame.K_m:
                        state = "MENU"

                elif state in ["GAMEOVER", "VICTORY"]:
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        if state == "VICTORY":
                            wave_num += 1
                            start_game(reset_all=False)
                        else:
                            start_game(reset_all=True)
                    elif event.key == pygame.K_m:
                        state = "MENU"

        # ----------------------------------------------------------------------
        # LOGIKA PERMAINAN (PLAYING)
        # ----------------------------------------------------------------------
        if state == "PLAYING":
            keys = pygame.key.get_pressed()
            dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
            paddle.move(dx)
            paddle.update()

            if keys[pygame.K_SPACE] and paddle.can_shoot():
                lasers.extend(paddle.shoot())
                snd.play("laser")

            if overdrive_timer > 0:
                overdrive_timer -= 1

            # Update Lasers
            for l in lasers[:]:
                l.update()
                if l.rect.bottom < 60:
                    lasers.remove(l)
                    continue
                for b in bricks[:]:
                    if l.rect.colliderect(b.rect):
                        fx.spawn_burst(l.rect.centerx, l.rect.top, COLOR_LASER, count=8)
                        snd.play("brick")
                        if b.hit(1):
                            score += b.points
                            high_score = max(high_score, score)
                            bricks.remove(b)
                        if l in lasers:
                            lasers.remove(l)
                        break

            # Update Capsules
            for cap in capsules[:]:
                cap.update()
                if cap.rect.colliderect(paddle.rect):
                    snd.play("powerup")
                    if cap.p_type == "EXPAND":
                        paddle.expand_timer = 480
                    elif cap.p_type == "LASER":
                        paddle.laser_timer = 420
                    elif cap.p_type == "MULTI" and len(balls) < 4:
                        balls.append(Ball(paddle.rect.centerx, paddle.rect.top - 10, speed=balls[0].speed))
                    elif cap.p_type == "HEAL":
                        lives = min(5, lives + 1)
                    capsules.remove(cap)
                elif cap.rect.top > SCREEN_HEIGHT:
                    capsules.remove(cap)

            # Update Balls
            for ball in balls[:]:
                ball.overdrive = (overdrive_timer > 0)
                ball.update()

                # Tabrakan Paddle
                if ball.rect.colliderect(paddle.rect) and ball.vy > 0:
                    offset_hit = (ball.x - paddle.rect.centerx) / (paddle.width / 2)
                    ball.vx = offset_hit * 8.0
                    ball.vy = -abs(ball.vy)
                    combo = 0
                    fx.spawn_burst(ball.x, paddle.rect.top, COLOR_PADDLE, count=10)
                    snd.play("paddle")

                # Tabrakan Bata
                for brick in bricks[:]:
                    if ball.rect.colliderect(brick.rect):
                        if not ball.overdrive:
                            prev_x = ball.x - ball.vx
                            if prev_x + ball.radius <= brick.rect.left or prev_x - ball.radius >= brick.rect.right:
                                ball.vx *= -1
                            else:
                                ball.vy *= -1

                        combo += 1
                        max_combo = max(max_combo, combo)
                        cyber_energy = min(100, cyber_energy + 6)
                        dmg = 4 if ball.overdrive else 1
                        destroyed = brick.hit(dmg)
                        fx.spawn_burst(ball.x, ball.y, brick.base_color, count=18, ring=destroyed)
                        snd.play("brick")

                        if destroyed:
                            score += brick.points * combo
                            high_score = max(high_score, score)
                            fx.shaker.trigger(6, 4)
                            if random.random() < 0.20:
                                p_choice = random.choice(list(POWERUP_TYPES.keys()))
                                capsules.append(PowerUpCapsule(brick.rect.centerx, brick.rect.centery, p_choice))
                            bricks.remove(brick)
                        break

                if ball.y > SCREEN_HEIGHT:
                    balls.remove(ball)

            # Kondisi Bola Habis
            if len(balls) == 0:
                lives -= 1
                combo = 0
                fx.shaker.trigger(12, 7)
                if lives <= 0:
                    state = "GAMEOVER"
                    snd.play("gameover")
                else:
                    current_speed = BALL_BASE_SPEED + (wave_num - 1) * 0.6
                    balls = [Ball(speed=current_speed)]

            # Kondisi Level Cleared
            if len(bricks) == 0:
                state = "VICTORY"
                snd.play("victory")

        # ----------------------------------------------------------------------
        # RENDERING LAYER
        # ----------------------------------------------------------------------
        screen.fill(COLOR_BG)
        cam_offset = fx.update_and_draw(screen) if state in ["PLAYING", "GAMEOVER", "VICTORY"] else (0, 0)
        draw_cyber_grid(screen, cam_offset)

        if state in ["PLAYING", "PAUSED", "GAMEOVER", "VICTORY"]:
            for b in bricks:
                b.draw(screen, cam_offset)
            for cap in capsules:
                cap.draw(screen, small_font, cam_offset)
            for l in lasers:
                l.draw(screen, cam_offset)
            paddle.draw(screen, cam_offset)
            for ball in balls:
                ball.draw(screen, cam_offset)

            # HUD TOP BAR
            pygame.draw.rect(screen, (14, 10, 30), (0, 0, SCREEN_WIDTH, 60))
            pygame.draw.line(screen, COLOR_PADDLE, (0, 60), (SCREEN_WIDTH, 60), 2)

            screen.blit(font.render(f"SCORE: {score}", True, COLOR_TEXT), (20, 20))
            screen.blit(font.render(f"WAVE: {wave_num}", True, COLOR_ACCENT), (180, 20))
            screen.blit(font.render(f"COMBO: x{combo}", True, (0, 255, 220) if combo > 1 else COLOR_MUTED), (280, 20))

            # Overdrive Energy Bar
            pygame.draw.rect(screen, (40, 30, 70), (410, 22, 160, 16), border_radius=4)
            bar_w = int(1.6 * (overdrive_timer / 3.6 if overdrive_timer > 0 else cyber_energy))
            bar_c = (0, 255, 230) if cyber_energy >= 100 or overdrive_timer > 0 else COLOR_PADDLE
            pygame.draw.rect(screen, bar_c, (410, 22, max(0, min(160, bar_w)), 16), border_radius=4)
            od_label = "SHIFT: BURST!" if cyber_energy >= 100 else ("OVERDRIVE" if overdrive_timer > 0 else "BURST GAUGE")
            screen.blit(small_font.render(od_label, True, COLOR_TEXT), (580, 23))

            # Lives indicator
            lives_str = "♦ " * lives
            screen.blit(font.render(f"HP: {lives_str}", True, COLOR_RED), (SCREEN_WIDTH - 130, 20))

        # ----------------------------------------------------------------------
        # STATE SCREEN OVERLAYS
        # ----------------------------------------------------------------------
        if state == "MENU":
            # Floating glow title
            pulse_offset = int(math.sin(title_pulse) * 6)
            glow_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*COLOR_PADDLE, 35), (SCREEN_WIDTH // 2, 220), 220)
            screen.blit(glow_surf, (0, 0))

            t_main = title_font.render("NEKOBREAKER", True, (245, 240, 255))
            t_sub = font.render("⚡ CYBER OVERDRIVE ⚡", True, COLOR_ACCENT)
            t_author = small_font.render("DESIGNED BY HEYDEN ALYAS", True, COLOR_MUTED)

            screen.blit(t_main, (SCREEN_WIDTH // 2 - t_main.get_width() // 2, 150 + pulse_offset))
            screen.blit(t_sub, (SCREEN_WIDTH // 2 - t_sub.get_width() // 2, 225))
            screen.blit(t_author, (SCREEN_WIDTH // 2 - t_author.get_width() // 2, 255))

            # Menu Box
            box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 220, 310, 440, 260)
            pygame.draw.rect(screen, (16, 12, 34), box_rect, border_radius=12)
            pygame.draw.rect(screen, COLOR_PADDLE, box_rect, width=2, border_radius=12)

            btn1 = font.render("[SPASI / ENTER]  MULAI PERMAINAN", True, COLOR_TEXT)
            btn2 = font.render("[H]              PANDUAN & KONTROL", True, COLOR_TEXT)
            snd_status = "AKTIF" if snd.enabled else "MATI"
            btn3 = font.render(f"[M]              AUDIO SFX: {snd_status}", True, COLOR_TEXT)
            btn4 = font.render("[ESC]            KELUAR KE DESKTOP", True, COLOR_MUTED)
            screen.blit(btn1, (box_rect.x + 35, box_rect.y + 40))
            screen.blit(btn2, (box_rect.x + 35, box_rect.y + 90))
            screen.blit(btn3, (box_rect.x + 35, box_rect.y + 140))
            screen.blit(btn4, (box_rect.x + 35, box_rect.y + 190))

            hs_text = font.render(f"RECORD TERTINGGI: {high_score}", True, COLOR_GOLD)
            screen.blit(hs_text, (SCREEN_WIDTH // 2 - hs_text.get_width() // 2, 600))

        elif state == "CONTROLS":
            ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            ov.fill((8, 6, 18, 235))
            screen.blit(ov, (0, 0))

            card = pygame.Rect(SCREEN_WIDTH // 2 - 280, 70, 560, 540)
            pygame.draw.rect(screen, (16, 12, 36), card, border_radius=12)
            pygame.draw.rect(screen, COLOR_ACCENT, card, width=2, border_radius=12)

            c_title = big_font.render("PANDUAN KONTROL", True, COLOR_ACCENT)
            screen.blit(c_title, (card.centerx - c_title.get_width() // 2, card.y + 25))

            lines = [
                ("KONTROL UTAMA:", COLOR_GOLD),
                ("• [A] / [D] atau [PANAH KIRI/KANAN] : Gerakkan Cyber Paddle", COLOR_TEXT),
                ("• [SPASI] : Tembak Dual Cannon (saat power-up GUN aktif)", COLOR_TEXT),
                ("• [LEFT SHIFT] : Aktifkan CYBER BURST saat gauge 100%", COLOR_TEXT),
                ("• [P] / [ESC] : Pause permainan kapan saja", COLOR_TEXT),
                ("", COLOR_TEXT),
                ("KAPSUL POWER-UP:", COLOR_GOLD),
                ("• [WIDE] : Memperlebar ukuran paddle sebesar 45%", POWERUP_TYPES["EXPAND"]["color"]),
                ("• [GUN]  : Memasang meriam ganda penembak bata", POWERUP_TYPES["LASER"]["color"]),
                ("• [x2]   : Menggandakan jumlah bola di arena", POWERUP_TYPES["MULTI"]["color"]),
                ("• [+1]   : Memulihkan 1 HP paddle", POWERUP_TYPES["HEAL"]["color"]),
                ("", COLOR_TEXT),
                ("Tekan [ESC] atau [SPASI] untuk Kembali ke Menu", COLOR_ACCENT),
            ]
            cur_y = card.y + 90
            for line, col in lines:
                surf = font.render(line, True, col)
                screen.blit(surf, (card.x + 35, cur_y))
                cur_y += 30

        elif state == "PAUSED":
            ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            ov.fill((8, 6, 18, 200))
            screen.blit(ov, (0, 0))

            p_box = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 140, 400, 280)
            pygame.draw.rect(screen, (18, 14, 38), p_box, border_radius=12)
            pygame.draw.rect(screen, COLOR_PADDLE, p_box, width=2, border_radius=12)

            t_pause = big_font.render("GAME DI-PAUSE", True, COLOR_PADDLE)
            screen.blit(t_pause, (p_box.centerx - t_pause.get_width() // 2, p_box.y + 30))

            m1 = font.render("[P]  LANJUTKAN (RESUME)", True, COLOR_TEXT)
            m2 = font.render("[R]  RESTART WAVE INI", True, COLOR_TEXT)
            m3 = font.render("[M]  MENU UTAMA", True, COLOR_MUTED)
            screen.blit(m1, (p_box.x + 50, p_box.y + 110))
            screen.blit(m2, (p_box.x + 50, p_box.y + 160))
            screen.blit(m3, (p_box.x + 50, p_box.y + 210))

        elif state == "GAMEOVER":
            ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            ov.fill((8, 6, 18, 225))
            screen.blit(ov, (0, 0))

            t1 = big_font.render("SYSTEM CORE DEPLETED", True, COLOR_RED)
            t_score = font.render(f"SKOR AKHIR: {score}   |   KOMBO TERTINGGI: x{max_combo}", True, COLOR_TEXT)
            t_hs = font.render(f"RECORD TERTINGGI: {high_score}", True, COLOR_GOLD)
            t2 = font.render("Tekan [SPASI] untuk Main Lagi  |  [M] Menu Utama", True, COLOR_ACCENT)

            screen.blit(t1, (SCREEN_WIDTH // 2 - t1.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
            screen.blit(t_score, (SCREEN_WIDTH // 2 - t_score.get_width() // 2, SCREEN_HEIGHT // 2 - 10))
            screen.blit(t_hs, (SCREEN_WIDTH // 2 - t_hs.get_width() // 2, SCREEN_HEIGHT // 2 + 25))
            screen.blit(t2, (SCREEN_WIDTH // 2 - t2.get_width() // 2, SCREEN_HEIGHT // 2 + 75))

        elif state == "VICTORY":
            ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            ov.fill((8, 6, 18, 220))
            screen.blit(ov, (0, 0))

            t1 = big_font.render(f"CYBER WAVE {wave_num} CLEARED!", True, COLOR_ACCENT)
            t_score = font.render(f"SKOR SAAT INI: {score}   |   KOMBO: x{combo}", True, COLOR_TEXT)
            t2 = font.render(f"Tekan [SPASI] Lanjut ke Wave {wave_num + 1}  |  [M] Menu Utama", True, COLOR_GOLD)

            screen.blit(t1, (SCREEN_WIDTH // 2 - t1.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            screen.blit(t_score, (SCREEN_WIDTH // 2 - t_score.get_width() // 2, SCREEN_HEIGHT // 2 + 5))
            screen.blit(t2, (SCREEN_WIDTH // 2 - t2.get_width() // 2, SCREEN_HEIGHT // 2 + 55))

        pygame.display.flip()

if __name__ == "__main__":
    main()
