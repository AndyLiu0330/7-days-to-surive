import pygame
import random
import sys

pygame.mixer.init()
pygame.init()
night_music_loaded = False
WIDTH, HEIGHT = 800, 600
WHITE, RED, GREEN, BLACK, YELLOW, GRAY, ORANGE = (255, 255, 255), (200, 0, 0), (0, 200, 0), (0, 0, 0), (255, 255, 0), (50, 50, 50), (255, 165, 0)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Survival Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)
small_font = pygame.font.SysFont(None, 28)  # Smaller font



menu_background = pygame.image.load("surival game/img/menuB.png").convert()
menu_background = pygame.transform.scale(menu_background, (WIDTH, HEIGHT))

# player image
player_images = {
    
    "up": pygame.image.load("surival game/img/archer_front.png").convert_alpha(),
    "left": pygame.image.load("surival game/img/archer_left.png").convert_alpha(),
    "down": pygame.image.load("surival game/img/archer_back.png").convert_alpha(),
    "right": pygame.image.load("surival game/img/archer_right.png").convert_alpha()
}

arrow_images = {
    "up": pygame.image.load("surival game/img/arrowUp.png").convert_alpha(),
    "down": pygame.image.load("surival game/img/arrowDown.png").convert_alpha(),
    "left": pygame.image.load("surival game/img/arrow.png").convert_alpha(),
    "right": pygame.image.load("surival game/img/arrowRight.png").convert_alpha()
}

# Resize if needed
for key in arrow_images:
    arrow_images[key] = pygame.transform.scale(arrow_images[key], (40, 40))

tree_image = pygame.image.load("surival game/img/tree.png").convert_alpha()
tree_image = pygame.transform.scale(tree_image, (30, 50))
wall_image = pygame.image.load("surival game/img/wall.png").convert_alpha()
wall_image = pygame.transform.scale(wall_image, (40, 40))
# scale them all
for k in player_images:
    player_images[k] = pygame.transform.scale(player_images[k], (40, 40))

facing = "up"

def load_slime_frames(sheet, row=0, col_start=0, col_end=4, frame_width=32, frame_height=32):
    frames = []
    for i in range(col_start, col_end):
        frame = sheet.subsurface(pygame.Rect(i * frame_width, row * frame_height, frame_width, frame_height))
        frames.append(pygame.transform.scale(frame, (30, 30)))  # Match enemy size
    return frames

slime_sprite_sheet = pygame.image.load("surival game/img/Enemy.png").convert_alpha()
slime_frames = load_slime_frames(slime_sprite_sheet)


season_backgrounds = {
    "spring": pygame.image.load("surival game/img/day1.png").convert(),
    "summer": pygame.image.load("surival game/img/day2.png").convert(),
    "fall": pygame.image.load("surival game/img/day3.png").convert(),
    "winter": pygame.image.load("surival game/img/day4.png").convert()
}
# Optionally scale to fit screen size
for key in season_backgrounds:
    season_backgrounds[key] = pygame.transform.scale(season_backgrounds[key], (WIDTH, HEIGHT))

    
def get_season(day):
    # Each season lasts 2 in-game days (adjust as desired)
    season_cycle = ["spring", "summer", "fall", "winter"]
    index = (day // 2) % 4
    return season_cycle[index]

night_backgrounds = {
    "spring": pygame.image.load("surival game/img/background 1.png").convert(),
    "summer": pygame.image.load("surival game/img/background 2.png").convert(),
    "fall": pygame.image.load("surival game/img/background 3.png").convert(),
    "winter": pygame.image.load("surival game/img/background 4.png").convert()
}

# Resize to screen size
for key in night_backgrounds:
    night_backgrounds[key] = pygame.transform.scale(night_backgrounds[key], (WIDTH, HEIGHT))

meat_icons = {
    "rotten_meat": pygame.image.load("surival game/img/rottenM.jpg").convert_alpha(),
    "normal_meat": pygame.image.load("surival game/img/cookM.jpg").convert_alpha(),
    "rare_meat": pygame.image.load("surival game/img/rareM.jpg").convert_alpha(),
    "super_meat": pygame.image.load("surival game/img/superM.jpg").convert_alpha(),
    "wood": pygame.image.load("surival game/img/wood.jpg").convert_alpha()
}

# Resize them to fit inventory nicely
for key in meat_icons:
    meat_icons[key] = pygame.transform.scale(meat_icons[key], (30, 30))


shoot_sound = pygame.mixer.Sound("surival game/mus/shoot.mp3")
shoot_sound.set_volume(0.5)
wood_collect_sound = pygame.mixer.Sound("surival game/mus/collectWood.mp3")
wood_collect_sound.set_volume(0.5)  # Optional volume setting
click_sound = pygame.mixer.Sound("surival game/mus/click.mp3")
click_sound.set_volume(0.5)  # Adjust as needed
eat_sound = pygame.mixer.Sound("surival game/mus/eat.mp3")
eat_sound.set_volume(0.5)  # Adjust volume as needed

levelup_sound = pygame.mixer.Sound("surival game/mus/levelUp.mp3")
levelup_sound.set_volume(0.5) 

walk_sound = pygame.mixer.Sound("surival game/mus/walk.mp3")  # 請使用你的步行音效路徑
walk_sound.set_volume(0.3)  # 可調整音量
walk_channel = pygame.mixer.Channel(1) 


# At the top of your file, add this:
current_music = None
music_time = {
    "day": 0,
    "night": 0
}

last_is_daytime =0

day_count = 0
has_won = False


MENU, PLAYING, GAME_OVER, CONTROLS = 0, 1, 2, 3
LOADING = 4
game_state = MENU
start_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 30, 200, 50)
controls_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 30, 200, 50)
quit_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 90, 200, 50)

player = pygame.Rect(WIDTH//2, HEIGHT//2, 40, 40)
player_speed = 5
player_direction = (1, 0)

tree_respawn_timer = 0
tree_respawn_interval = 600  # 10 seconds at 60 FPS
max_trees = 5

walls = []  # List of wall rectangles
wall_size = 40
wall_lifetime = 0  # How many cycles walls have existed

pixel_font = pygame.font.Font("surival game/PressStart2P-Regular.ttf", 20)  # Adjust path and size


health = 100
hunger = 100
hunger_timer = 0

enemies = []
bullets = []

inventory = {
    "rotten_meat": 0,
    "normal_meat": 0,
    "rare_meat": 0,
    "super_meat": 0,
    "wood": 0
}
inventory_open = False
show_controls = False

# Load meat icons (place actual image files in the same folder or adjust path)

class Cloud:
    def __init__(self):
        self.image = pygame.image.load("surival game/img/cloud.png").convert_alpha()
        self.scale = random.uniform(0.5, 1.5)
        self.image = pygame.transform.scale(self.image, (int(100 * self.scale), int(60 * self.scale)))
        self.x = random.randint(-200, WIDTH)
        self.y = random.randint(30, 200)
        self.speed = random.uniform(0.2, 1.0)

    def update(self):
        self.x += self.speed
        if self.x > WIDTH + 100:
            self.x = -200
            self.y = random.randint(30, 200)
            self.speed = random.uniform(0.2, 1.0)
            self.scale = random.uniform(0.5, 1.5)
            self.image = pygame.transform.scale(pygame.image.load("surival game/img/cloud.png").convert_alpha(), (int(100 * self.scale), int(60 * self.scale)))

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))
        
# 初始化多個雲朵
clouds = [Cloud() for _ in range(5)]

class Petal:
    def __init__(self):
        self.original_image = pygame.image.load("surival game/img/petal.png").convert_alpha()
        self.scale = random.uniform(0.3, 0.8)
        self.image = pygame.transform.scale(
            self.original_image, (int(40 * self.scale), int(40 * self.scale))
        )
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)
        self.speed_y = random.uniform(0.5, 1.5)*5
        self.drift = random.uniform(-0.2, 0.2)

    def update(self):
        self.y += self.speed_y
        self.x += self.drift
        if self.y > HEIGHT:
            self.reset()

    def reset(self):
        self.scale = random.uniform(0.3, 0.8)
        self.image = pygame.transform.scale(
            self.original_image, (int(40 * self.scale), int(40 * self.scale))
        )
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-100, -40)
        self.speed_y = random.uniform(0.5, 1.5)
        self.drift = random.uniform(-0.3, 0.3)

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))
petals = [Petal() for _ in range(20)]

def add_meat():
    roll = random.random()
    if roll <= 0.1:
        inventory["super_meat"] += 1
    elif roll <= 0.6:
        inventory["normal_meat"] += 1
    else:
        inventory["rotten_meat"] += 1

def draw_inventory():
    pygame.draw.rect(screen, GRAY, (WIDTH - 260, 20, 240, 260))
    draw_text("Inventory", WIDTH - 250, 25)

    y_offset = 60
    for item, count in inventory.items():
        if count > 0:
            icon = meat_icons[item]
            # Draw the icon
            screen.blit(icon, (WIDTH - 250, y_offset))
            # Prepare text
            item_name = item.replace("_", " ").title()
            text = small_font.render(f"{item_name}: x {count}", True, WHITE)
            # Draw text next to icon
            screen.blit(text, (WIDTH - 210, y_offset + 5))  # +5 for vertical alignment
            y_offset += 40

def draw_controls():
    pygame.draw.rect(screen, GRAY, (20, 300, 350, 250))
    draw_text("Controls:", 30, 310)
    lines = [
        f"WASD: Move",
        f"Tab: Toggle Help",
        f"B: Open Inventory",
        f"1-4: Eat Meat",
        f"Mouse Left: Attack"
        f"F: Build Wall (day only, needs wood)",

    ]
    small_font = pygame.font.SysFont(None, 30)
    for i, line in enumerate(lines):
        text = small_font.render(line, True, YELLOW)
        screen.blit(text, (30, 340 + i * 30))

    # Add note for control customization
    small_font2 = pygame.font.SysFont(None, 24)
    change_note = small_font2.render("(Customize controls in future menu)", True, GRAY)
    screen.blit(change_note, (30, 340 + len(lines) * 30))

def draw_health_bar():
    pygame.draw.rect(screen, RED, (10, 10, 200, 20))
    pygame.draw.rect(screen, GREEN, (10, 10, 2 * max(0, health), 20))

    hp_text = pixel_font.render(f"HP: {health}%", True, BLACK if health > 50 else WHITE)
    screen.blit(hp_text, (10 + 100 - hp_text.get_width() // 2, 10))

    
    draw_text(f"Day {day_count}", 10, 130, WHITE)
    big_font = pygame.font.SysFont(None, 60)
    time_text = "Daytime" if is_daytime else "Nighttime"
    time_render = big_font.render(time_text, True, YELLOW)
    screen.blit(time_render, (WIDTH // 2 - time_render.get_width() // 2, 40))
    seconds_left = (day_length - day_timer) // 60
    draw_text(f"{seconds_left}s left", WIDTH // 2 - 40, 100, WHITE)



def draw_exp_bar():
    pygame.draw.rect(screen, GRAY, (10, 70, 200, 20))
    pygame.draw.rect(screen, YELLOW, (10, 70, 2 * (exp % 100), 20))
    draw_text(f"LV {level}", 220, 70)

def draw_hunger_bar():
    pygame.draw.rect(screen, RED, (10, 40, 200, 20))
    pygame.draw.rect(screen, ORANGE, (10, 40, 2 * max(0, hunger), 20))
    hunger_text = pixel_font.render(f"Hunger: {hunger}%", True, BLACK if hunger > 50 else WHITE)
    screen.blit(hunger_text, (10 + 100 - hunger_text.get_width() // 2, 40))

def draw_text(text, x, y, color=WHITE, center=False):
    rendered = pixel_font.render(text, True, color)
    if center:
        x -= rendered.get_width() // 2
    screen.blit(rendered, (x, y))

import math

# 選單角色位置與背景動畫參數
cloud_x = 0
menu_tip = random.choice([
    "Tip: Press F to build walls during the day.",
    "Hint: Rotten meat is not healthy.",
    "Advice: Survive for 7 days to win!"
])
menu_music_playing = False

def show_menu():
    global cloud_x, menu_music_playing


    # 播放背景音樂（只播放一次）
    if not menu_music_playing:
        pygame.mixer.music.load("surival game/mus/menu.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        menu_music_playing = True

    # 背景動畫（飄動的雲）
    season = get_season(day_count)
    screen.blit(season_backgrounds[season], (0, 0))
    for petal in petals:
        petal.update()
        petal.draw(screen)
        

    cloud_img = pygame.image.load("surival game/img/cloud.png").convert_alpha()
    cloud_img = pygame.transform.scale(cloud_img, (100, 60))
    screen.blit(cloud_img, (cloud_x, 50))
    cloud_x = (cloud_x + 1) % WIDTH

    
    # 主角站位動畫
    screen.blit(player_images["down"], (WIDTH//2 - 200, HEIGHT//2 - 40))

    # 浮動標題動畫
    t = pygame.time.get_ticks() / 500  # time-based offset
    offset = int(10 * math.sin(t))
    draw_text("7 Days to surive", WIDTH//2, HEIGHT//2 - 120 + offset, YELLOW, center=True)

    # 滑鼠座標
    mouse_pos = pygame.mouse.get_pos()

    # 按鈕區域
    pygame.draw.rect(screen, GRAY, (WIDTH//2 - 150, HEIGHT//2 - 80, 300, 220), border_radius=12)

    # Start Button
    start_color = GREEN if start_rect.collidepoint(mouse_pos) else WHITE
    pygame.draw.rect(screen, start_color, start_rect, border_radius=8)
    draw_text("Start", WIDTH//2, HEIGHT//2 - 20, BLACK, center=True)

    # Controls Button
    controls_color = ORANGE if controls_rect.collidepoint(mouse_pos) else WHITE
    pygame.draw.rect(screen, controls_color, controls_rect, border_radius=8)
    draw_text("Controls", WIDTH//2, HEIGHT//2 + 40, BLACK, center=True)

    # Quit Button
    quit_color = RED if quit_rect.collidepoint(mouse_pos) else WHITE
    pygame.draw.rect(screen, quit_color, quit_rect, border_radius=8)
    draw_text("Quit", WIDTH//2, HEIGHT//2 + 100, BLACK, center=True)

    # 隨機提示
    draw_text(menu_tip, WIDTH//2, HEIGHT - 40, GRAY, center=True)

    pygame.display.flip()

def show_game_over():
    # Dark translucent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    # Title text
    title_text = "You Survived 7 Days! You Win!" if has_won else "Game Over!"
    title_color = YELLOW if has_won else RED
    draw_text(title_text, WIDTH // 2, HEIGHT // 2 - 100, title_color, center=True)

    # Button setup
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()

    # Restart
    restart_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 30, 200, 50)
    restart_color = GREEN if restart_rect.collidepoint(mouse_pos) else WHITE
    pygame.draw.rect(screen, restart_color, restart_rect, border_radius=8)
    draw_text("Restart", WIDTH//2, HEIGHT//2 - 20, BLACK, center=True)

    # Main Menu
    menu_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 40, 200, 50)
    menu_color = ORANGE if menu_rect.collidepoint(mouse_pos) else WHITE
    pygame.draw.rect(screen, menu_color, menu_rect, border_radius=8)
    draw_text("Main Menu", WIDTH//2, HEIGHT//2 + 50, BLACK, center=True)

    # Quit
    quit_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 110, 200, 50)
    quit_color = RED if quit_rect.collidepoint(mouse_pos) else WHITE
    pygame.draw.rect(screen, quit_color, quit_rect, border_radius=8)
    draw_text("Quit", WIDTH//2, HEIGHT//2 + 120, BLACK, center=True)

    # Button click handling
    if mouse_click[0]:
        global game_state
        if restart_rect.collidepoint(mouse_pos):
            click_sound.play()
            game_state = PLAYING
            
            reset_game()
        elif menu_rect.collidepoint(mouse_pos):
            click_sound.play()
            game_state = MENU
        elif quit_rect.collidepoint(mouse_pos):
            click_sound.play()
            pygame.quit()
            sys.exit()


def show_loading_screen():
    screen.fill(BLACK)
    draw_text("Loading...", WIDTH // 2, HEIGHT // 2, YELLOW, center=True)
    pygame.display.flip()

def show_game_win():
    # Dimmed golden spring background
    win_bg = season_backgrounds["spring"].copy()
    golden_overlay = pygame.Surface((WIDTH, HEIGHT))
    golden_overlay.fill((255, 215, 0))  # gold tint
    golden_overlay.set_alpha(40)
    win_bg.blit(golden_overlay, (0, 0))
    screen.blit(win_bg, (0, 0))

    # Animated petals
    for petal in petals:
        petal.update()
        petal.draw(screen)

    # Victory title
    draw_text("You Survived All 7 Days!", WIDTH // 2, HEIGHT // 2 - 120, YELLOW, center=True)
    draw_text("You mastered the wild.", WIDTH // 2, HEIGHT // 2 - 70, WHITE, center=True)

    # Player victory pose
    screen.blit(player_images["up"], (WIDTH // 2 - 20, HEIGHT // 2 - 40))

    # Buttons
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()

    play_again_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50)
    menu_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 90, 200, 50)
    quit_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 160, 200, 50)

    pygame.draw.rect(screen, GREEN if play_again_rect.collidepoint(mouse_pos) else WHITE, play_again_rect, border_radius=8)
    draw_text("Play Again", WIDTH // 2, HEIGHT // 2 + 30, BLACK, center=True)

    pygame.draw.rect(screen, ORANGE if menu_rect.collidepoint(mouse_pos) else WHITE, menu_rect, border_radius=8)
    draw_text("Main Menu", WIDTH // 2, HEIGHT // 2 + 100, BLACK, center=True)

    pygame.draw.rect(screen, GRAY if quit_rect.collidepoint(mouse_pos) else WHITE, quit_rect, border_radius=8)
    draw_text("Quit", WIDTH // 2, HEIGHT // 2 + 170, BLACK, center=True)

    # Handle clicks
    if mouse_click[0]:
        global game_state
        if play_again_rect.collidepoint(mouse_pos):
            click_sound.play()
            game_state = PLAYING
            reset_game()
        elif menu_rect.collidepoint(mouse_pos):
            click_sound.play()
            game_state = MENU
        elif quit_rect.collidepoint(mouse_pos):
            click_sound.play()
            pygame.quit()
            sys.exit()

    pygame.display.flip()



def spawn_enemy():
    x = random.choice([0, WIDTH - 30])
    y = random.randint(0, HEIGHT - 30)
    enemy = pygame.Rect(x, y, 30, 30)
    enemies.append({"rect": enemy, "frame": 0, "timer": 0})

for enemy in enemies[:]:
    rect = enemy["rect"]

    # Movement toward player
    enemy_dx = 1 if rect.x < player.x else -1 if rect.x > player.x else 0
    enemy_dy = 1 if rect.y < player.y else -1 if rect.y > player.y else 0

    test_rect = rect.move(enemy_dx, enemy_dy)
    if not any(test_rect.colliderect(wall) for wall in walls):
        rect.x += enemy_dx
        rect.y += enemy_dy

    # Animation update
    enemy["timer"] += 1
    if enemy["timer"] >= 10:
        enemy["frame"] = (enemy["frame"] + 1) % len(slime_frames)
        enemy["timer"] = 0

    # Draw slime frame
    screen.blit(slime_frames[enemy["frame"]], rect.topleft)

    # Collision with player
    if player.colliderect(rect):
        health -= 1
        if health <= 0:
            game_state = GAME_OVER

    # Collision with bullets
    for bullet in bullets[:]:
        if rect.colliderect(bullet["rect"]):
            enemies.remove(enemy)
            bullets.remove(bullet)
            add_meat()
            exp += 10
            if exp % 100 == 0:
                level += 1
                level_up_flash_timer = 60
            break


def reset_game():
    global player, health, hunger, enemies, bullets, spawn_timer, inventory, inventory_open, hunger_timer, player_direction, show_controls, exp, level, level_up_flash_timer
    player = pygame.Rect(WIDTH//2, HEIGHT//2, 40, 40)
    health = 100
    hunger = 100
    enemies.clear()
    bullets.clear()
    inventory = {"rotten_meat": 0, "normal_meat": 0, "rare_meat": 0, "super_meat": 0, "wood": 0}
    inventory_open = False
    spawn_timer = 0

day_length = 600  # frames (~10 seconds)
day_timer = 0
is_daytime = True

trees = []
for _ in range(5):
    tree = pygame.Rect(random.randint(50, WIDTH - 100), random.randint(50, HEIGHT - 100), 30, 50)
    trees.append(tree)
    hunger_timer = 0
    player_direction = (1, 0)
    show_controls = False
    exp = 0
    level = 1
    level_up_flash_timer = 0

spawn_timer = 0
running = True
while running:
    clock.tick(60)

    if game_state == MENU:
        show_menu()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_rect.collidepoint(event.pos):
                    click_sound.play()
                    game_state = LOADING
                    loading_start_time = pygame.time.get_ticks() 
                elif controls_rect.collidepoint(event.pos):
                    game_state = CONTROLS
                    click_sound.play()

                elif quit_rect.collidepoint(event.pos):
                    pygame.quit()
                    click_sound.play()

                    sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_state = PLAYING
                    reset_game()
                elif event.key == pygame.K_ESCAPE:
                    running = False

    elif game_state == CONTROLS:
        screen.fill(BLACK)
        draw_controls()
        draw_text("Press ESC to return to menu", WIDTH//2 - 150, HEIGHT - 50, GRAY, center=True)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = MENU

    elif game_state == GAME_OVER:
        if has_won:
            show_game_win()
        else:
            show_game_over()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game_state = PLAYING
                    reset_game()    
                if pygame.time.get_ticks() - loading_start_time > 2000:  # 2秒後切換
                    reset_game()
  
                elif event.key == pygame.K_ESCAPE:
                    running = False
        pygame.display.flip()
        
    elif game_state == LOADING:
        show_loading_screen()
        menu_music_playing = False  # Stop menu music if it was playing
        
        if pygame.time.get_ticks() - loading_start_time > 2000:  # 2 秒後切換
            game_state = GAME_OVER
        
        if pygame.time.get_ticks() - loading_start_time > 2000:  # 2秒後切換
            reset_game()
            game_state = PLAYING        
                # Wait for 1.5 seconds (1500 ms)
        

    elif game_state == PLAYING:

        day_timer += 1

    


        if day_timer >= day_length:
            is_daytime = not is_daytime
            day_timer = 0
            wall_lifetime += 1
        
        

        if last_is_daytime == False and is_daytime == True:
             day_count += 1
        last_is_daytime = is_daytime

        if wall_lifetime >= 2:
            walls.clear()
            wall_lifetime = 0

        if day_count > 7 and not has_won:
            has_won = True
            game_state = GAME_OVER
        
        if current_music == "day":
            music_time["day"] += 1  # Each frame at 60 FPS ≈ 1/60 seconds
        elif current_music == "night":
            music_time["night"] += 1

        if is_daytime and current_music != "day":
            pygame.mixer.music.load("surival game/mus/dayBGM.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1, music_time["day"] / 60)
            current_music = "day"
        elif not is_daytime and current_music != "night":
            pygame.mixer.music.load("surival game/mus/Pixel Night Fight.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1, music_time["night"] / 60)
            current_music = "night"

    # ALL remaining game update + render code
    # must also be indented here

        if is_daytime:
            season = get_season(day_count)
            screen.blit(season_backgrounds[season], (0, 0))
        else:
            screen.blit(night_backgrounds[season], (0, 0))




        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w]:
            dy = -1
            facing = "up"
        if keys[pygame.K_s]:
            dy = 1
            facing = "down"
        if keys[pygame.K_a]:
            dx = -1
            facing = "left"
        if keys[pygame.K_d]:
            dx = 1
            facing = "right"
        if (dx != 0 or dy != 0):
            if not walk_channel.get_busy():
                walk_channel.play(walk_sound, loops=-1)
        else:
            walk_channel.stop()

        if dx != 0 or dy != 0:
            player_direction = (dx, dy)

        player.x += dx * player_speed
        player.y += dy * player_speed
        player.x = max(0, min(player.x, WIDTH - player.width))
        player.y = max(0, min(player.y, HEIGHT - player.height))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    inventory_open = not inventory_open
                elif event.key == pygame.K_TAB:
                    pass  # We check this key in real-time during PLAYING state
                elif event.key == pygame.K_1 and inventory["rotten_meat"] > 0:
                    eat_sound.play()
                    hunger = min(100, hunger + 5)
                    health = max(0, health - 10)
                    inventory["rotten_meat"] -= 1
                elif event.key == pygame.K_2 and inventory["normal_meat"] > 0:
                    eat_sound.play()
                    hunger = min(100, hunger + 5)
                    inventory["normal_meat"] -= 1
                elif event.key == pygame.K_3 and inventory["rare_meat"] > 0:
                    eat_sound.play()
                    hunger = min(100, hunger + 10)
                    inventory["rare_meat"] -= 1
                elif event.key == pygame.K_4 and inventory["super_meat"] > 0:
                    eat_sound.play()
                    hunger = min(100, hunger + 20)
                    inventory["super_meat"] -= 1
                elif event.key == pygame.K_e:
                    for tree in trees[:]:
                        if player.colliderect(tree):
                            trees.remove(tree)
                            inventory["wood"] += 1
                            wood_collect_sound.play()
                elif event.key == pygame.K_f and is_daytime and inventory["wood"] > 0:
                    offset_x = player_direction[0] * wall_size
                    offset_y = player_direction[1] * wall_size
                    wall_x = player.x + offset_x
                    wall_y = player.y + offset_y
                    new_wall = pygame.Rect(wall_x, wall_y, wall_size, wall_size)

                    if not any(wall.colliderect(new_wall) for wall in walls):
                            walls.append(new_wall)
                            inventory["wood"] -= 1


            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                arrow_size = 40  # match the arrow image size

                bullet = {
                    "rect": pygame.Rect(player.centerx - arrow_size // 2, player.centery - arrow_size // 2, arrow_size, arrow_size),
                    "dir": player_direction,
                    "facing": facing
                }
                bullets.append(bullet)
                shoot_sound.play()

        hunger_timer += 1
        if hunger_timer >= 60:
            if hunger > 0:
                hunger -= 1
            else:
                health -= 1
            if health < 100 and hunger >= 2:
                health = min(100, health + 1)
                hunger -= 2
            hunger_timer = 0
            if health <= 0:
                game_state = GAME_OVER

        spawn_timer += 1
        if not is_daytime and spawn_timer >= 60:
            spawn_enemy()
            spawn_timer = 0
        tree_respawn_timer += 1
        if tree_respawn_timer >= tree_respawn_interval:
                if len(trees) < max_trees:
                    new_tree = pygame.Rect(random.randint(50, WIDTH - 100), random.randint(50, HEIGHT - 100), 30, 50)
                    trees.append(new_tree)
                    tree_respawn_timer = 0

        

        for bullet in bullets[:]:
            dx, dy = bullet["dir"]
            bullet["rect"].x += dx * 10
            bullet["rect"].y += dy * 10
            screen.blit(arrow_images[bullet["facing"]], bullet["rect"].topleft)
            if bullet["rect"].x < 0 or bullet["rect"].x > WIDTH or bullet["rect"].y < 0 or bullet["rect"].y > HEIGHT:
                bullets.remove(bullet)

        for enemy in enemies[:]:
            rect = enemy["rect"]

            # Movement toward player
            enemy_dx = 1 if rect.x < player.x else -1 if rect.x > player.x else 0
            enemy_dy = 1 if rect.y < player.y else -1 if rect.y > player.y else 0

            test_rect = rect.move(enemy_dx, enemy_dy)
            if not any(test_rect.colliderect(wall) for wall in walls):
                rect.x += enemy_dx
                rect.y += enemy_dy

            # Animation update
            enemy["timer"] += 1
            if enemy["timer"] >= 10:
                enemy["frame"] = (enemy["frame"] + 1) % len(slime_frames)
                enemy["timer"] = 0

            # Draw slime frame
            screen.blit(slime_frames[enemy["frame"]], rect.topleft)

            # Collision with player
            if player.colliderect(rect):
                health -= 1
                if health <= 0:
                    game_state = GAME_OVER

            # Collision with bullets
            for bullet in bullets[:]:
                if rect.colliderect(bullet["rect"]):
                    enemies.remove(enemy)
                    bullets.remove(bullet)
                    add_meat()
                    exp += 10
                    if exp % 100 == 0:
                        level += 1
                        level_up_flash_timer = 60
                        levelup_sound.play()    
                    break


        if level_up_flash_timer > 0:
            flash_text = pixel_font.render("LEVEL UP!", True, (255, 255, 0))
            screen.blit(flash_text, (player.x - 20, player.y - 30))
            screen.blit(player_images[facing], player.topleft)
            level_up_flash_timer -= 1
        else:
            screen.blit(player_images[facing], player.topleft)
        draw_health_bar()
        draw_hunger_bar()
        draw_exp_bar()

        # Draw trees during the day
        if is_daytime:
            for tree in trees:
                screen.blit(tree_image, tree.topleft)
                if player.colliderect(tree):
                    draw_text("Press E to collect wood", player.x - 20, player.y - 30, YELLOW,  center=False)
        # Draw walls
        for wall in walls:
            screen.blit(wall_image, wall.topleft)
        if inventory_open:
            draw_inventory()
        if pygame.key.get_pressed()[pygame.K_TAB]:
            draw_controls()
        
        

        pygame.display.flip()

pygame.quit()
