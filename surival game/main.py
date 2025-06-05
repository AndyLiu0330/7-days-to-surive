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

# player image
player_images = {
    
    "up": pygame.image.load("img/archer_front.png").convert_alpha(),
    "left": pygame.image.load("img/archer_left.png").convert_alpha(),
    "down": pygame.image.load("img/archer_back.png").convert_alpha(),
    "right": pygame.image.load("img/archer_right.png").convert_alpha()
}

arrow_images = {
    "up": pygame.image.load("img/arrowUp.png").convert_alpha(),
    "down": pygame.image.load("img/arrowDown.png").convert_alpha(),
    "left": pygame.image.load("img/arrow.png").convert_alpha(),
    "right": pygame.image.load("img/arrowRight.png").convert_alpha()
}

# Resize if needed
for key in arrow_images:
    arrow_images[key] = pygame.transform.scale(arrow_images[key], (20, 20))

tree_image = pygame.image.load("img/tree.png").convert_alpha()
tree_image = pygame.transform.scale(tree_image, (30, 50))
wall_image = pygame.image.load("img/wall.png").convert_alpha()
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

slime_sprite_sheet = pygame.image.load("img/Enemy.png").convert_alpha()
slime_frames = load_slime_frames(slime_sprite_sheet)


season_backgrounds = {
    "spring": pygame.image.load("img/day1.png").convert(),
    "summer": pygame.image.load("img/day2.png").convert(),
    "fall": pygame.image.load("img/day3.png").convert(),
    "winter": pygame.image.load("img/day4.png").convert()
}
# Optionally scale to fit screen size
for key in season_backgrounds:
    season_backgrounds[key] = pygame.transform.scale(season_backgrounds[key], (WIDTH, HEIGHT))

    
def get_season(day):
    # Each season lasts 2 in-game days (adjust as desired)
    season_cycle = ["spring", "summer", "fall", "winter"]
    index = (day // 2) % 4
    return season_cycle[index]

meat_icons = {
    "rotten_meat": pygame.image.load("img/rottenM.jpg").convert_alpha(),
    "normal_meat": pygame.image.load("img/cookM.jpg").convert_alpha(),
    "rare_meat": pygame.image.load("img/rareM.jpg").convert_alpha(),
    "super_meat": pygame.image.load("img/superM.jpg").convert_alpha(),
    "wood": pygame.image.load("img/wood.jpg").convert_alpha()
}

# Resize them to fit inventory nicely
for key in meat_icons:
    meat_icons[key] = pygame.transform.scale(meat_icons[key], (30, 30))


shoot_sound = pygame.mixer.Sound("mus/shoot.mp3")
shoot_sound.set_volume(0.5)
wood_collect_sound = pygame.mixer.Sound("mus/collectWood.mp3")
wood_collect_sound.set_volume(0.5)  # Optional volume setting
click_sound = pygame.mixer.Sound("mus/click.mp3")
click_sound.set_volume(0.5)  # Adjust as needed
eat_sound = pygame.mixer.Sound("mus/eat.mp3")
eat_sound.set_volume(0.5)  # Adjust volume as needed




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

pixel_font = pygame.font.Font("PressStart2P-Regular.ttf", 20)  # Adjust path and size


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

def draw_text(text, x, y, color=WHITE):
    rendered = pixel_font.render(text, True, color)
    screen.blit(rendered, (x, y))

def show_menu():
    screen.fill((135, 206, 235) if is_daytime else (20, 20, 50))
    pygame.draw.rect(screen, GRAY, (WIDTH//2 - 150, HEIGHT//2 - 100, 300, 220), border_radius=12)
    draw_text("2D Survival Game", WIDTH//2 - 110, HEIGHT//2 - 80, YELLOW)

    mouse_pos = pygame.mouse.get_pos()

    # Start Button
    pygame.draw.rect(screen, GREEN if start_rect.collidepoint(mouse_pos) else WHITE, start_rect, border_radius=8)
    draw_text("Start", WIDTH//2 - 30, HEIGHT//2 - 20, BLACK)

    # Controls Button
    pygame.draw.rect(screen, ORANGE if controls_rect.collidepoint(mouse_pos) else WHITE, controls_rect, border_radius=8)
    draw_text("Controls", WIDTH//2 - 50, HEIGHT//2 + 40, BLACK)

    # Quit Button
    pygame.draw.rect(screen, RED if quit_rect.collidepoint(mouse_pos) else WHITE, quit_rect, border_radius=8)
    draw_text("Quit", WIDTH//2 - 30, HEIGHT//2 + 100, BLACK)

    pygame.display.flip()

def show_game_over():
    screen.fill((135, 206, 235) if is_daytime else (20, 20, 50))
    if has_won:
        draw_text("You Survived 7 Days! You Win!", WIDTH//2 - 200, HEIGHT//2 - 120, YELLOW)
    else:
        draw_text("Game Over!", WIDTH//2 - 100, HEIGHT//2 - 120, RED)


    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()

    # Restart Button
    restart_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 60, 200, 50)
    pygame.draw.rect(screen, GREEN if restart_rect.collidepoint(mouse_pos) else WHITE, restart_rect, border_radius=8)
    draw_text("Restart", WIDTH//2 - 50, HEIGHT//2 - 50, BLACK)

    # Main Menu Button
    menu_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 10, 200, 50)
    pygame.draw.rect(screen, ORANGE if menu_rect.collidepoint(mouse_pos) else WHITE, menu_rect, border_radius=8)
    draw_text("Main Menu", WIDTH//2 - 60, HEIGHT//2 + 20, BLACK)

    

    # Quit Button
    quit_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 80, 200, 50)
    pygame.draw.rect(screen, RED if quit_rect.collidepoint(mouse_pos) else WHITE, quit_rect, border_radius=8)
    draw_text("Quit", WIDTH//2 - 30, HEIGHT//2 + 90, BLACK)

    if mouse_click[0]:
        global game_state
        if restart_rect.collidepoint(mouse_pos):
            game_state = PLAYING
            reset_game()
        elif menu_rect.collidepoint(mouse_pos):
            game_state = MENU
        elif quit_rect.collidepoint(mouse_pos):
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
                    game_state = PLAYING
                    reset_game()
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
        draw_text("Press ESC to return to menu", WIDTH//2 - 150, HEIGHT - 50, GRAY)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = MENU

    elif game_state == GAME_OVER:
        show_game_over()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game_state = PLAYING
                    reset_game()
                elif event.key == pygame.K_ESCAPE:
                    running = False

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
            pygame.mixer.music.load("mus/dayBGM.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1, music_time["day"] / 60)
            current_music = "day"
        elif not is_daytime and current_music != "night":
            pygame.mixer.music.load("mus/Pixel Night Fight.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1, music_time["night"] / 60)
            current_music = "night"

    # ALL remaining game update + render code
    # must also be indented here

        if is_daytime:
            season = get_season(day_count)
            screen.blit(season_backgrounds[season], (0, 0))
        else:
            screen.fill((20, 20, 50))  # or load a night background if you have one




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
                bullet = {
                    "rect": pygame.Rect(player.centerx - 5, player.centery - 5, 10, 10),
                    "dir": player_direction,
                    "facing": facing  # Save string direction like "up", "down", etc.
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
                    break


        if level_up_flash_timer > 0:
            pygame.draw.rect(screen, (255, 255, 255), player)
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
                    draw_text("Press E to collect wood", player.x - 20, player.y - 30, YELLOW)
        # Draw walls
        for wall in walls:
            screen.blit(wall_image, wall.topleft)
        if inventory_open:
            draw_inventory()
        if pygame.key.get_pressed()[pygame.K_TAB]:
            draw_controls()
        
        

        pygame.display.flip()

pygame.quit()
