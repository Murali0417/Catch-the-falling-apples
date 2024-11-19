import pygame
import random
import sys
import time

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Catch the Falling Apples")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

basket_width, basket_height = 200, 200
basket_speed = 10

apple_width, apple_height = 40, 40
apple_speed = 5
level = 1

level_thresholds = [10, 20, 30, 40, 50]

STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
STATE_PAUSED = "paused"
state = STATE_MENU

score = 0
missed_apples = 0
max_misses = 5
basket_x = WIDTH // 2 - basket_width // 2
basket_y = HEIGHT - basket_height - 10
apple_x = random.randint(0, WIDTH - apple_width)
apple_y = 0
running = True
clock = pygame.time.Clock()
start_time = None

background_image = pygame.image.load("background.jpg")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
basket_image = pygame.image.load("basket.png")
basket_image = pygame.transform.scale(basket_image, (basket_width, basket_height))
apple_image = pygame.image.load("apple.png")
apple_image = pygame.transform.scale(apple_image, (apple_width, apple_height))

pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.set_volume(0.5)
catch_sound = pygame.mixer.Sound("catch_sound.wav")
catch_sound.set_volume(0.7)
miss_sound = pygame.mixer.Sound("miss_sound.wav")
miss_sound.set_volume(0.7)

pygame.mixer.music.play(-1)

def reset_game():
    global score, missed_apples, basket_x, apple_x, apple_y, apple_speed, level, start_time
    score = 0
    level = 1
    missed_apples = 0
    apple_speed = 5
    basket_x = WIDTH // 2 - basket_width // 2
    apple_x = random.randint(0, WIDTH - apple_width)
    apple_y = 0
    start_time = time.time()

def increase_level():
    global level, apple_speed, basket_width
    level += 1
    apple_speed += 1
    basket_width = max(100, basket_width - 10)

def draw_text(text, font, color, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    screen.blit(text_obj, text_rect)

def draw_button(text, x, y, width, height):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    is_hovered = x < mouse[0] < x + width and y < mouse[1] < y + height
    color = GRAY if is_hovered else WHITE
    pygame.draw.rect(screen, color, (x, y, width, height), 5)
    draw_text(text, font, BLACK, x + width // 2, y + height // 2)
    if is_hovered and click[0] == 1:
        pygame.time.delay(200)
        return True
    return False

while running:
    screen.fill(WHITE)
    screen.blit(background_image, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if state == STATE_MENU:
        draw_text("Catch the Falling Apples", large_font, BLACK, WIDTH // 2, HEIGHT // 4)
        if draw_button("Start Game", WIDTH // 2 - 100, HEIGHT // 2, 200, 50):
            reset_game()
            state = STATE_PLAYING
        if draw_button("Quit", WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50):
            running = False

    elif state == STATE_PLAYING:
        elapsed_time = int(time.time() - start_time)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and basket_x > 0:
            basket_x -= basket_speed
        if keys[pygame.K_RIGHT] and basket_x < WIDTH - basket_width:
            basket_x += basket_speed

        apple_y += apple_speed

        if (apple_y + apple_height > basket_y and
            apple_x + apple_width > basket_x and
            apple_x < basket_x + basket_width):
            score += 1
            catch_sound.play()
            apple_x = random.randint(0, WIDTH - apple_width)
            apple_y = 0

        if apple_y > HEIGHT:
            miss_sound.play()
            missed_apples += 1
            apple_x = random.randint(0, WIDTH - apple_width)
            apple_y = 0
            if missed_apples >= max_misses:
                state = STATE_GAME_OVER

        if score in level_thresholds and level_thresholds.index(score) + 1 > level - 1:
            increase_level()

        scaled_basket_image = pygame.transform.scale(basket_image, (basket_width, basket_height))
        screen.blit(scaled_basket_image, (basket_x, basket_y))

        fill_height = (missed_apples / max_misses) * basket_height
        pygame.draw.rect(screen, RED, (basket_x, basket_y + basket_height - fill_height, basket_width, fill_height))

        screen.blit(apple_image, (apple_x, apple_y))

        score_text = font.render(f"Score: {score}", True, BLACK)
        level_text = font.render(f"Level: {level}", True, BLACK)
        timer_text = font.render(f"Time: {elapsed_time}s", True, BLACK)
        chances_text = font.render(f"Chances Left: {max_misses - missed_apples}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 40))
        screen.blit(timer_text, (10, 70))
        screen.blit(chances_text, (10, 100))

        if draw_button("Pause", WIDTH - 110, 10, 100, 50):
            state = STATE_PAUSED

    elif state == STATE_GAME_OVER:
        draw_text("Game Over!", large_font, BLACK, WIDTH // 2, HEIGHT // 4)
        draw_text(f"Final Score: {score}", font, BLACK, WIDTH // 2, HEIGHT // 2)
        if draw_button("Retry", WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50):
            reset_game()
            state = STATE_PLAYING
        if draw_button("Main Menu", WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 50):
            state = STATE_MENU

    elif state == STATE_PAUSED:
        draw_text("Paused", large_font, BLACK, WIDTH // 2, HEIGHT // 4)
        if draw_button("Resume", WIDTH - 110, HEIGHT // 2, 100, 50):
            state = STATE_PLAYING
        if draw_button("Quit to Menu", WIDTH - 110, HEIGHT // 2 + 60, 100, 50):
            state = STATE_MENU

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
