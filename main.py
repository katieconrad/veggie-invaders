import pygame
import random
from characters import Character, Scoreboard

# Initialize game and key elements
pygame.init()
screen_size = (1400, 1000)
screen = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()
background = pygame.Surface(screen_size)
font = pygame.font.SysFont("arial", 72)
score_font = pygame.font.SysFont("arial", 40)
scoreboard = Scoreboard(score_font)
pause = False

# Initialize sounds
cat_hit_sound = pygame.mixer.Sound("./sounds/hit_meow.ogg")
veg_hit_sound = pygame.mixer.Sound("./sounds/splat.wav")
pew_sound = pygame.mixer.Sound("./sounds/pew.wav")
cow_hit_sound = pygame.mixer.Sound("./sounds/moo.aiff")

# Get display dimensions
screen_width = screen.get_width()
screen_height = screen.get_height()

# Create player sprite
player_x = round(screen_width / 2)
player_y = screen_height - 150
cat = Character("./images/Cat sprite big.png", screen, screen_width, screen_height, "player", player_x, player_y, 10, 0)
char = pygame.sprite.Group()
char.add(cat)

# Create enemy group and variables
enemies = pygame.sprite.Group()
enemy_start_y = 100
enemy_dir = "L"

# Create cow group and variables
cow_group = pygame.sprite.Group()
cow = 0


def create_enemies(y_value):
    """Creates enemies"""
    enemy_images = ["./images/apple.png", "./images/egg.png", "./images/mushroom.png", "./images/tomato.png", "./images/wheat.png"]
    enemy_score = 60
    enemy_y = y_value
    for i in range(0, 5):
        img = random.choice(enemy_images)
        enemy_x = 300
        enemy_score -= 10
        for n in range(0, 11):
            new_enemy = Character(img, screen, screen_width, screen_height, "enemy", enemy_x, enemy_y, 1, enemy_score)
            enemy_x += 75
            enemies.add(new_enemy)
        enemy_y += 75


def game_over():
    """displays game over screen"""
    over_text_width, over_text_height = font.size("GAME OVER")
    game_over_text = font.render("GAME OVER", True, "white")
    restart_text_width, restart_text_height = score_font.size("press Y to restart")
    restart_text = score_font.render("press Y to restart", True, "white")
    for e in enemies:
        e.kill()
    enemies.clear(screen, background)
    cat.kill()
    cat.lives = 3
    cat.score = 0
    over_text_x = round((screen_width / 2) - (over_text_width / 2))
    over_text_y = round((screen_height / 2) - (over_text_height / 2))
    restart_text_x = round((screen_width / 2) - (restart_text_width / 2))
    restart_text_y = over_text_y + 100
    screen.blit(game_over_text, (over_text_x, over_text_y))
    screen.blit(restart_text, (restart_text_x, restart_text_y))


def pause_game():
    """displays pause screen"""
    text_width, text_height = font.size("PAUSE")
    pause_text = font.render("PAUSE", True, "white")
    screen.blit(pause_text, (round((screen_width / 2) - (text_width / 2)), round((screen_height / 2) - (text_height / 2))))


def reset_game():
    """Resets game to start"""
    enemies.empty()
    if cat.game_over:
        cat.game_over = False
    create_enemies(enemy_start_y)
    return True


running = reset_game()

# Create game loop
while running:

    # Check events for quit or pause
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            # Change pause state
            if event.key == pygame.K_RETURN:
                if pause:
                    pause = False
                else:
                    pause = True

    # Fill screen with black
    screen.fill("black")

    # If music not playing, start music
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load("./sounds/melody.wav")
        pygame.mixer.music.play(-1)

    # Event listener for key press
    keys = pygame.key.get_pressed()

    # Game over
    if cat.game_over:
        if keys[pygame.K_y]:
            enemy_start_y = 100
            if cow != 0:
                cow.kill()
                cow = 0
            reset_game()
        else:
            game_over()

    # Pause game
    elif pause:
        pause_game()

    # If no enemies, create new enemies but lower
    elif len(enemies) == 0:
        if enemy_start_y <= 450:
            enemy_start_y += 50
        else:
            enemy_start_y = 100
        if cat.lives < 3:
            cat.lives += 1
        reset_game()

    else:
        # Display enemies
        enemies.draw(screen)

        # Display scoreboard
        score = scoreboard.update(cat.score)
        life_text_width, life_score = scoreboard.life_update(cat.lives)
        screen.blit(score, (cat.min_x, 30))
        screen.blit(life_score, (cat.max_x - life_text_width, 30))

        # Player character movement
        if keys[pygame.K_a]:
            cat.move_left()
        if keys[pygame.K_d]:
            cat.move_right()
        screen.blit(cat.image, (cat.rect.x, cat.rect.y))

        # Detect player shooting
        if keys[pygame.K_SPACE]:
            new_paw = cat.paw_swipe()
            if new_paw:
                pygame.mixer.Sound.play(pew_sound)

        # Enemies have chance to shoot
        for enemy in enemies:
            shot_chance = random.randint(0, 3500)
            if shot_chance == 1:
                enemy.paw_swipe()
            if enemy.paw != 0:
                # Display weapon
                screen.blit(enemy.paw.image, (enemy.paw.rect.x, enemy.paw.rect.y))

                # Check for collisions between weapon and cat
                kill_check = pygame.sprite.collide_rect(enemy.paw, cat)
                # If hit, cat dies
                if kill_check:
                    pygame.mixer.Sound.play(cat_hit_sound)
                    enemy.paw.kill()
                    enemy.paw = 0
                    cat.lose_life()
                    # If no lives, game over
                    if cat.game_over:
                        game_over()

                # If no collision, move paw
                else:
                    enemy.paw = enemy.paw.move()

        # If cat died, update display
        if cat.dead:
            cat.update()

        else:

            if cat.paw != 0:
                # Display paw
                screen.blit(cat.paw.image, (cat.paw.rect.x, cat.paw.rect.y))

                # Check for collisions between paw and enemies
                collided_enemy = pygame.sprite.spritecollideany(cat.paw, enemies)
                # If enemy is hit, update game
                if collided_enemy:
                    pygame.mixer.Sound.play(veg_hit_sound)
                    cat.score += collided_enemy.score
                    collided_enemy.kill()
                    cat.paw = 0
                    enemies.clear(screen, background)
                    enemies.draw(screen)
                    # Increase enemy speed at intervals
                    if len(enemies) == 33 or len(enemies) == 11:
                        for enemy in enemies:
                            enemy.speed += 1

                # If no collision, move paw
                else:
                    cat.paw = cat.paw.move()

            # Enemy movement
            # If enemies are at bottom of screen, game ends
            enemy_y_list = [enemy.rect.y for enemy in enemies]
            if any(y >= cat.rect.y for y in enemy_y_list):
                cat.game_over = True
                game_over()
            # Enemies move left until they hit screen edge, then down and reverse direction
            else:
                enemy_x_list = [enemy.rect.x for enemy in enemies]
                if enemy_dir == "L":
                    if any(x <= cat.min_x for x in enemy_x_list):
                        for enemy in enemies:
                            enemy.move_down()
                        enemy_dir = "R"
                    else:
                        for enemy in enemies:
                            enemy.move_left()
                # Enemies move right until they hit screen edge, then down and reverse direction
                else:
                    if any(x >= cat.max_x for x in enemy_x_list):
                        for enemy in enemies:
                            enemy.move_down()
                        enemy_dir = "L"
                    else:
                        for enemy in enemies:
                            enemy.move_right()

                # Update enemy display
                enemies.clear(screen, background)
                enemies.draw(screen)

            # Random chance for cow to appear
            if cow == 0:
                cow_chance = random.randint(0, 1250)
                if cow_chance == 1:
                    cow_scores = [50, 100, 150, 200, 300]
                    cow_score = random.choice(cow_scores)
                    cow = Character("./images/cow.png", screen, screen_width, screen_height, "cow", 0, 65, 3, cow_score)
                    cow_group.add(cow)

            else:
                # Cow moves across screen
                if cow.rect.x < cow.max_x:
                    cow.move_right()
                # Cow disappears at edge of screen
                else:
                    cow.kill()
                    cow.dead = True
                    cow_group.clear(screen, background)
                    cow_group.draw(screen)

                # If cat paw is active, check for collision between paw and cow
                if cat.paw != 0:
                    cow_kill_check = pygame.sprite.collide_rect(cat.paw, cow)
                    # If cow is hit, remove cow
                    if cow_kill_check:
                        pygame.mixer.Sound.play(cow_hit_sound)
                        cat.paw.kill()
                        cat.paw = 0
                        cat.score += cow.score
                        cow.kill()
                        cow_group.clear(screen, background)
                        cow_group.draw(screen)

                # If cow is hit, reset cow stats
                if cow.dead:
                    cow.dead = False
                    cow = 0

            # Display cow
            cow_group.draw(screen)

    # Refresh screen
    pygame.display.flip()

    # Frame rate
    clock.tick(60)

# Quit game when loop ends
pygame.quit()
