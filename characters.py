import pygame


class Character(pygame.sprite.Sprite):

    def __init__(self, img, display, width, height, char, start_x, start_y, speed, score):
        super().__init__()
        self.life_image = pygame.image.load(img).convert()
        self.image = self.life_image
        self.speed = speed
        self.screen_width = width
        self.screen_height = height
        self.max_x = width - 100
        self.min_x = 100
        self.screen = display
        self.score = score
        self.paw_x = 0
        self.paw_y = 0
        self.paw = 0
        self.char_type = char
        self.rect = self.image.get_rect()
        self.rect.x = start_x
        self.rect.y = start_y
        self.direction = "left"
        self.lives = 3
        self.dead = False
        self.death_img = pygame.image.load("./images/x.png").convert()
        self.death_frames = 20
        self.death_count = 0
        self.game_over = False

    def move_left(self):
        """Moves character to screen left"""
        if self.rect.x > self.min_x:
            self.rect.x -= self.speed
        return self.rect.x, self.rect.y

    def move_right(self):
        """Moves character to screen right"""
        if self.rect.x < self.max_x:
            self.rect.x += self.speed
        return self.rect.x, self.rect.y

    def move_down(self):
        """Moves character down"""
        self.rect.y += 30

    def paw_swipe(self):
        """Character shoots weapon"""
        if self.paw == 0:
            self.paw_x = self.rect.centerx - 10
            self.paw_y = self.rect.centery
            if self.char_type == "player":
                img = "./images/paw.png"
            else:
                img = "./images/seed.png"
            self.paw = Weapon(img, self.screen, self.screen_width, self.screen_height, self.char_type, self.paw_x, self.paw_y)
            if self.char_type == "player":
                return True

    def lose_life(self):
        """Character loses a life"""
        self.lives -= 1
        if self.lives == 0:
            self.game_over = True
        else:
            self.dead = True

    def update(self):
        """Updates character if dead"""
        if self.dead:
            self.image = self.death_img
            if self.death_count < self.death_frames:
                self.death_count += 1
            else:
                self.image = self.life_image
                self.dead = False
                self.death_count = 0


class Weapon(pygame.sprite.Sprite):

    def __init__(self, img, display, width, height, char, start_x, start_y):
        super().__init__()
        self.image = pygame.image.load(img).convert()
        self.speed = 10
        self.screen_width = width
        self.screen_height = height
        self.weapon_type = char
        self.screen = display
        self.rect = self.image.get_rect()
        self.rect.x = start_x
        self.rect.y = start_y

    def move(self):
        """Paw moves up screen/enemy weapon moves down screen"""
        if self.weapon_type == "player":
            self.rect.y -= self.speed
            if self.rect.y <= 0:
                return 0
            else:
                return self
        else:
            self.rect.y += self.speed
            if self.rect.y >= self.screen_height:
                return 0
            else:
                return self


class Scoreboard:
    def __init__(self, font):
        self.font = font

    def update(self, score):
        """Updates score display"""
        score_text = self.font.render(f"Score: {score}", True, "white")
        return score_text

    def life_update(self, lives):
        """Updates life display"""
        text_width, text_height = self.font.size(f"Lives: {lives}")
        life_text = self.font.render(f"Lives: {lives}", True, "white")
        return text_width, life_text
