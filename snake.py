
import pygame
import random
import sys
import os
import numpy as np
import math

# ==================== INITIAL SETUP ====================
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

WIDTH, HEIGHT = 640, 640
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

# Colors
BG_COLOR = (12, 14, 22)
GRID_COLOR = (28, 32, 48)
SNAKE_HEAD = (80, 255, 160)
SNAKE_BODY_1 = (40, 200, 120)
SNAKE_BODY_2 = (30, 160, 95)
SNAKE_GHOST = (170, 110, 255)
FOOD_GOLD = (255, 215, 60)
POWER_SLOW = (70, 160, 255)
POWER_GHOST = (180, 90, 255)
WALL_COLOR = (255, 130, 50)
WALL_BORDER = (200, 80, 20)
TEXT_WHITE = (240, 240, 245)
TEXT_GOLD = (255, 210, 70)
TEXT_GRAY = (160, 165, 180)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game - Power Ups Edition")
clock = pygame.time.Clock()

# ==================== LOAD IMAGES ====================
def load_image(name, size=None):
    """Load image and optionally scale it. Returns None if not found."""
    try:
        img = pygame.image.load(name).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img
    except Exception as e:
        print(f"Could not load {name}: {e}")
        return None

# Window icon (scaled to 64x64)
icon_img = load_image("snake_icon.png", (64, 64))
if icon_img:
    pygame.display.set_icon(icon_img)

# Apple image for normal food (scaled to fit grid)
apple_img = load_image("apple.png", (GRID_SIZE - 2, GRID_SIZE - 2))

# Fonts
font = pygame.font.SysFont("segoeui", 26)
big_font = pygame.font.SysFont("segoeui", 68, bold=True)
medium_font = pygame.font.SysFont("segoeui", 34)
small_font = pygame.font.SysFont("segoeui", 20)

# ==================== SOUND ====================
def generate_sound(frequency=440, duration=0.15, volume=0.4, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = np.sin(2 * np.pi * frequency * t)
    decay = np.linspace(1, 0.08, wave.shape[0])
    wave = wave * decay
    audio = (wave * volume * 32767).astype(np.int16)
    stereo_audio = np.column_stack((audio, audio))
    return pygame.sndarray.make_sound(stereo_audio)

eat_sound = generate_sound(680, 0.11, 0.5)
gameover_sound = generate_sound(200, 0.45, 0.55)
countdown_sound = generate_sound(900, 0.09, 0.3)
power_sound = generate_sound(540, 0.16, 0.45)
gold_sound = generate_sound(820, 0.14, 0.55)

# ==================== HIGH SCORE ====================
HIGHSCORE_FILE = "highscore.txt"

def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                return int(f.read().strip())
        except:
            return 0
    return 0

def save_highscore(score):
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(score))


# ==================== SNAKE ====================
class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.length = 3
        center = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.positions = [center]
        self.direction = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
        self.score = 0
        self.grow = False
        self.ghost_mode = False
        self.ghost_timer = 0
        self.slow_mode = False
        self.slow_timer = 0

    def get_head_position(self):
        return self.positions[0]

    def update(self, walls):
        head = self.get_head_position()

        if head in walls and not self.ghost_mode:
            return False

        dx, dy = self.direction
        new_head = ((head[0] + dx) % GRID_WIDTH, (head[1] + dy) % GRID_HEIGHT)

        if new_head in self.positions[1:] and not self.ghost_mode:
            return False
        if new_head in walls and not self.ghost_mode:
            return False

        self.positions.insert(0, new_head)

        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False
            self.length += 1

        return True

    def turn(self, direction):
        if (direction[0] * -1, direction[1] * -1) == self.direction:
            return
        self.direction = direction

    def draw(self, surface):
        for i, pos in enumerate(self.positions):
            x = pos[0] * GRID_SIZE
            y = pos[1] * GRID_SIZE
            rect = pygame.Rect(x + 1, y + 1, GRID_SIZE - 2, GRID_SIZE - 2)

            if i == 0:
                color = SNAKE_GHOST if self.ghost_mode else SNAKE_HEAD
                pygame.draw.rect(surface, color, rect, border_radius=7)

                glow = pygame.Surface((GRID_SIZE + 8, GRID_SIZE + 8), pygame.SRCALPHA)
                pygame.draw.circle(glow, (*color, 40), (GRID_SIZE // 2 + 4, GRID_SIZE // 2 + 4), GRID_SIZE // 2 + 3)
                surface.blit(glow, (x - 4, y - 4))

                eye_size = 3
                if self.direction == (0, -1):
                    eye1, eye2 = (x + 6, y + 6), (x + 13, y + 6)
                elif self.direction == (0, 1):
                    eye1, eye2 = (x + 6, y + 12), (x + 13, y + 12)
                elif self.direction == (-1, 0):
                    eye1, eye2 = (x + 6, y + 6), (x + 6, y + 13)
                else:
                    eye1, eye2 = (x + 13, y + 6), (x + 13, y + 13)

                pygame.draw.circle(surface, (255, 255, 255), eye1, eye_size)
                pygame.draw.circle(surface, (255, 255, 255), eye2, eye_size)
                pygame.draw.circle(surface, (20, 20, 30), eye1, 1)
                pygame.draw.circle(surface, (20, 20, 30), eye2, 1)
            else:
                if self.ghost_mode:
                    color = (150, 95, 230) if i % 2 == 0 else (120, 70, 200)
                else:
                    color = SNAKE_BODY_1 if i % 2 == 0 else SNAKE_BODY_2
                pygame.draw.rect(surface, color, rect, border_radius=5)


# ==================== FOOD ====================
class Food:
    def __init__(self):
        self.position = (0, 0)
        self.is_golden = False
        self.pulse = 0
        self.randomize()

    def randomize(self, snake_positions=None, walls=None):
        while True:
            self.position = (random.randint(0, GRID_WIDTH - 1),
                             random.randint(0, GRID_HEIGHT - 1))
            if snake_positions and self.position in snake_positions:
                continue
            if walls and self.position in walls:
                continue
            break
        self.is_golden = random.random() < 0.22

    def update(self):
        self.pulse += 0.12

    def draw(self, surface):
        x = self.position[0] * GRID_SIZE
        y = self.position[1] * GRID_SIZE

        if self.is_golden:
            # Golden food stays procedural (nice glow)
            cx = x + GRID_SIZE // 2
            cy = y + GRID_SIZE // 2
            radius = GRID_SIZE // 2 - 2 + int(math.sin(self.pulse) * 1.5)
            glow = pygame.Surface((GRID_SIZE * 2, GRID_SIZE * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 215, 60, 55), (GRID_SIZE, GRID_SIZE), radius + 6)
            surface.blit(glow, (cx - GRID_SIZE, cy - GRID_SIZE))
            pygame.draw.circle(surface, FOOD_GOLD, (cx, cy), radius)
            pygame.draw.circle(surface, (255, 255, 200), (cx - 3, cy - 3), 3)
        else:
            # Normal food uses the apple image
            if apple_img:
                surface.blit(apple_img, (x + 1, y + 1))
            else:
                # Fallback if image not found
                cx = x + GRID_SIZE // 2
                cy = y + GRID_SIZE // 2
                pygame.draw.circle(surface, (255, 70, 80), (cx, cy), GRID_SIZE // 2 - 2)


# ==================== POWER-UP ====================
class PowerUp:
    def __init__(self):
        self.position = None
        self.type = None
        self.active = False
        self.timer = 0
        self.pulse = 0

    def spawn(self, snake_positions, food_pos, walls):
        if self.active or random.random() > 0.012:
            return
        for _ in range(30):
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in snake_positions and pos != food_pos and pos not in walls:
                self.position = pos
                self.type = random.choice(["slow", "ghost"])
                self.active = True
                self.timer = 380
                break

    def update(self):
        if self.active:
            self.timer -= 1
            self.pulse += 0.15
            if self.timer <= 0:
                self.active = False
                self.position = None

    def draw(self, surface):
        if not self.active:
            return
        cx = self.position[0] * GRID_SIZE + GRID_SIZE // 2
        cy = self.position[1] * GRID_SIZE + GRID_SIZE // 2
        radius = GRID_SIZE // 2 - 2 + int(math.sin(self.pulse) * 1.8)
        color = POWER_SLOW if self.type == "slow" else POWER_GHOST

        glow = pygame.Surface((GRID_SIZE * 2, GRID_SIZE * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*color[:3], 55), (GRID_SIZE, GRID_SIZE), radius + 5)
        surface.blit(glow, (cx - GRID_SIZE, cy - GRID_SIZE))
        pygame.draw.circle(surface, color, (cx, cy), radius)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 4)


# ==================== MOVING WALLS ====================
class MovingWalls:
    def __init__(self, count=5):
        self.walls = []
        self.directions = []
        self.move_counter = 0
        for _ in range(count):
            pos = (random.randint(3, GRID_WIDTH - 4), random.randint(3, GRID_HEIGHT - 4))
            self.walls.append(pos)
            self.directions.append(random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)]))

    def update(self):
        self.move_counter += 1
        if self.move_counter < 2:
            return
        self.move_counter = 0

        new_walls = []
        for i, (wx, wy) in enumerate(self.walls):
            dx, dy = self.directions[i]
            nx = (wx + dx) % GRID_WIDTH
            ny = (wy + dy) % GRID_HEIGHT
            if random.random() < 0.06:
                self.directions[i] = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            new_walls.append((nx, ny))
        self.walls = new_walls

    def draw(self, surface):
        for wx, wy in self.walls:
            rect = pygame.Rect(wx * GRID_SIZE + 1, wy * GRID_SIZE + 1, GRID_SIZE - 2, GRID_SIZE - 2)
            pygame.draw.rect(surface, WALL_COLOR, rect, border_radius=4)
            pygame.draw.rect(surface, WALL_BORDER, rect, 2, border_radius=4)


# ==================== MAIN ====================
def main():
    snake = Snake()
    food = Food()
    power = PowerUp()
    walls = MovingWalls(count=5)
    highscore = load_highscore()

    game_state = "countdown"
    countdown_number = 3
    countdown_timer = 0
    base_speed = 9.0
    speed = base_speed

    while True:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if game_state == "gameover" and event.key == pygame.K_r:
                    snake.reset()
                    food.randomize()
                    power.active = False
                    walls = MovingWalls(count=5)
                    game_state = "countdown"
                    countdown_number = 3
                    countdown_timer = 0
                    speed = base_speed
                    continue

                if game_state == "playing":
                    if event.key in (pygame.K_UP, pygame.K_w):
                        snake.turn((0, -1))
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        snake.turn((0, 1))
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        snake.turn((-1, 0))
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        snake.turn((1, 0))

        if game_state == "countdown":
            countdown_timer += dt
            if countdown_timer >= 750:
                countdown_timer = 0
                countdown_number -= 1
                if countdown_number > 0:
                    countdown_sound.play()
                else:
                    game_state = "playing"
                    countdown_sound.play()

        elif game_state == "playing":
            if snake.ghost_mode:
                snake.ghost_timer -= 1
                if snake.ghost_timer <= 0:
                    snake.ghost_mode = False
            if snake.slow_mode:
                snake.slow_timer -= 1
                if snake.slow_timer <= 0:
                    snake.slow_mode = False

            walls.update()
            food.update()
            power.update()

            if not snake.update(walls.walls):
                game_state = "gameover"
                gameover_sound.play()
                if snake.score > highscore:
                    highscore = snake.score
                    save_highscore(highscore)

            if snake.get_head_position() == food.position:
                snake.grow = True
                points = 30 if food.is_golden else 10
                snake.score += points
                if food.is_golden:
                    gold_sound.play()
                else:
                    eat_sound.play()
                food.randomize(snake.positions, walls.walls)
                speed = min(speed + 0.35, 15.5)

            if power.active and snake.get_head_position() == power.position:
                power_sound.play()
                if power.type == "slow":
                    snake.slow_mode = True
                    snake.slow_timer = 170
                else:
                    snake.ghost_mode = True
                    snake.ghost_timer = 140
                power.active = False
                power.position = None

            power.spawn(snake.positions, food.position, walls.walls)

        # Drawing
        screen.fill(BG_COLOR)

        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y), 1)

        walls.draw(screen)
        snake.draw(screen)
        food.draw(screen)
        power.draw(screen)

        score_text = font.render(f"Score  {snake.score}", True, TEXT_WHITE)
        high_text = font.render(f"Best  {highscore}", True, TEXT_GOLD)
        length_text = small_font.render(f"Length  {snake.length}", True, TEXT_GRAY)

        screen.blit(score_text, (14, 12))
        screen.blit(high_text, (14, 42))
        screen.blit(length_text, (14, 74))

        status_y = 108
        if snake.ghost_mode:
            t = small_font.render(f"GHOST  {max(0, snake.ghost_timer // 10)}", True, POWER_GHOST)
            screen.blit(t, (14, status_y))
            status_y += 24
        if snake.slow_mode:
            t = small_font.render(f"SLOW  {max(0, snake.slow_timer // 10)}", True, POWER_SLOW)
            screen.blit(t, (14, status_y))

        if game_state == "countdown":
            if countdown_number > 0:
                count_text = big_font.render(str(countdown_number), True, TEXT_GOLD)
            else:
                count_text = big_font.render("GO!", True, SNAKE_HEAD)
            screen.blit(count_text, (WIDTH // 2 - count_text.get_width() // 2,
                                     HEIGHT // 2 - count_text.get_height() // 2))

        if game_state == "gameover":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((8, 10, 18, 180))
            screen.blit(overlay, (0, 0))

            over_text = big_font.render("GAME OVER", True, (255, 80, 90))
            restart_text = medium_font.render("Press R to Restart", True, TEXT_WHITE)
            screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 90))
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 5))

            if snake.score >= highscore and snake.score > 0:
                record = medium_font.render("NEW HIGH SCORE!", True, TEXT_GOLD)
                screen.blit(record, (WIDTH // 2 - record.get_width() // 2, HEIGHT // 2 + 55))

        pygame.display.flip()

        if game_state == "playing":
            current_speed = speed * 0.55 if snake.slow_mode else speed
            pygame.time.delay(max(7, int(1000 / current_speed) - 16))


if __name__ == "__main__":
    main()
