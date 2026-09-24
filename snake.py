
import pygame
import random
import sys
import os
import numpy as np

# --- تنظیمات اولیه ---
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

# رنگ‌ها
BLACK = (15, 15, 25)
WHITE = (255, 255, 255)
GREEN = (50, 205, 50)
DARK_GREEN = (34, 139, 34)
HEAD_GREEN = (0, 255, 100)
RED = (255, 60, 60)
GRAY = (40, 40, 55)
GOLD = (255, 215, 0)
EYE_WHITE = (255, 255, 255)
EYE_BLACK = (20, 20, 20)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game - Improved")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 28)
big_font = pygame.font.SysFont("arial", 72)
medium_font = pygame.font.SysFont("arial", 40)
small_font = pygame.font.SysFont("arial", 24)

# --- ساخت صدا ---
def generate_sound(frequency=440, duration=0.15, volume=0.4, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = np.sin(2 * np.pi * frequency * t)
    decay = np.linspace(1, 0.1, wave.shape[0])
    wave = wave * decay
    audio = (wave * volume * 32767).astype(np.int16)
    stereo_audio = np.column_stack((audio, audio))
    return pygame.sndarray.make_sound(stereo_audio)

eat_sound = generate_sound(frequency=660, duration=0.12, volume=0.5)
gameover_sound = generate_sound(frequency=220, duration=0.4, volume=0.6)
countdown_sound = generate_sound(frequency=880, duration=0.1, volume=0.3)

# --- High Score ---
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


# --- کلاس مار ---
class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.length = 3
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
        self.score = 0
        self.grow = False

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        head = self.get_head_position()
        x, y = self.direction
        new_head = ((head[0] + x) % GRID_WIDTH, (head[1] + y) % GRID_HEIGHT)

        if new_head in self.positions[1:]:
            return False

        self.positions.insert(0, new_head)

        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False
            self.length += 1
            self.score += 10

        return True

    def turn(self, direction):
        if (direction[0] * -1, direction[1] * -1) == self.direction:
            return
        self.direction = direction

    def draw(self, surface):
        for i, pos in enumerate(self.positions):
            x = pos[0] * GRID_SIZE
            y = pos[1] * GRID_SIZE
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)

            if i == 0:  # سر مار
                pygame.draw.rect(surface, HEAD_GREEN, rect, border_radius=6)
                
                # چشم‌ها
                eye_size = 4
                if self.direction == (0, -1):      # بالا
                    eye1 = (x + 5, y + 5)
                    eye2 = (x + 11, y + 5)
                elif self.direction == (0, 1):     # پایین
                    eye1 = (x + 5, y + 11)
                    eye2 = (x + 11, y + 11)
                elif self.direction == (-1, 0):    # چپ
                    eye1 = (x + 5, y + 5)
                    eye2 = (x + 5, y + 11)
                else:                              # راست
                    eye1 = (x + 11, y + 5)
                    eye2 = (x + 11, y + 11)

                pygame.draw.circle(surface, EYE_WHITE, eye1, eye_size)
                pygame.draw.circle(surface, EYE_WHITE, eye2, eye_size)
                pygame.draw.circle(surface, EYE_BLACK, eye1, 2)
                pygame.draw.circle(surface, EYE_BLACK, eye2, 2)

            else:  # بدن
                color = DARK_GREEN if i % 2 == 0 else GREEN
                pygame.draw.rect(surface, color, rect, border_radius=4)


class Food:
    def __init__(self):
        self.position = (0, 0)
        self.randomize()

    def randomize(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))

    def draw(self, surface):
        x = self.position[0] * GRID_SIZE + GRID_SIZE // 2
        y = self.position[1] * GRID_SIZE + GRID_SIZE // 2
        pygame.draw.circle(surface, RED, (x, y), GRID_SIZE // 2 - 2)
        pygame.draw.circle(surface, (255, 150, 150), (x - 3, y - 3), 3)  # درخشش


def main():
    snake = Snake()
    food = Food()
    highscore = load_highscore()

    # وضعیت‌های بازی
    game_state = "countdown"   # countdown | playing | gameover
    countdown_number = 3
    countdown_timer = 0
    speed = 10

    while True:
        dt = clock.tick(60)  # برای کنترل زمان شمارش معکوس

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if game_state == "gameover":
                    if event.key == pygame.K_r:
                        snake.reset()
                        food.randomize()
                        game_state = "countdown"
                        countdown_number = 3
                        countdown_timer = 0
                        speed = 10
                    continue

                if game_state == "playing":
                    if event.key == pygame.K_UP:
                        snake.turn((0, -1))
                    elif event.key == pygame.K_DOWN:
                        snake.turn((0, 1))
                    elif event.key == pygame.K_LEFT:
                        snake.turn((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        snake.turn((1, 0))

        # --- منطق شمارش معکوس ---
        if game_state == "countdown":
            countdown_timer += dt
            if countdown_timer >= 800:  # هر ۰.۸ ثانیه یک عدد
                countdown_timer = 0
                countdown_number -= 1
                if countdown_number > 0:
                    countdown_sound.play()
                else:
                    game_state = "playing"
                    countdown_sound.play()

        # --- منطق بازی ---
        elif game_state == "playing":
            if not snake.update():
                game_state = "gameover"
                gameover_sound.play()
                if snake.score > highscore:
                    highscore = snake.score
                    save_highscore(highscore)

            if snake.get_head_position() == food.position:
                snake.grow = True
                food.randomize()
                while food.position in snake.positions:
                    food.randomize()
                eat_sound.play()
                speed = min(speed + 0.35, 17)

        # --- رسم صفحه ---
        screen.fill(BLACK)

        # شبکه ملایم
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y), 1)

        snake.draw(screen)
        food.draw(screen)

        # امتیازها
        score_text = font.render(f"Score: {snake.score}", True, WHITE)
        high_text = font.render(f"High Score: {highscore}", True, GOLD)
        length_text = small_font.render(f"Length: {snake.length}", True, (180, 180, 180))

        screen.blit(score_text, (10, 10))
        screen.blit(high_text, (10, 42))
        screen.blit(length_text, (10, 74))

        # شمارش معکوس
        if game_state == "countdown":
            if countdown_number > 0:
                count_text = big_font.render(str(countdown_number), True, GOLD)
            else:
                count_text = big_font.render("GO!", True, GREEN)
            
            screen.blit(count_text, (WIDTH // 2 - count_text.get_width() // 2,
                                     HEIGHT // 2 - count_text.get_height() // 2))

        # صفحه Game Over
        if game_state == "gameover":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            over_text = big_font.render("GAME OVER", True, RED)
            restart_text = medium_font.render("Press R to Restart", True, WHITE)

            screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 80))
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10))

            if snake.score >= highscore and snake.score > 0:
                new_record = medium_font.render("NEW HIGH SCORE!", True, GOLD)
                screen.blit(new_record, (WIDTH // 2 - new_record.get_width() // 2, HEIGHT // 2 + 70))

        pygame.display.flip()

        # کنترل سرعت فقط در حالت بازی
        if game_state == "playing":
            pygame.time.delay(max(10, int(1000 / speed) - 16))


if __name__ == "__main__":
    main()
