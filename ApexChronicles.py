import pygame
import random
import time

# Initialize Pygame
pygame.init()
pygame.font.init() # Initialize font module
pygame.mixer.init() # Initialize mixer for sound

# MODIFIED: Define a base resolution. All game logic and assets are based on these dimensions.
BASE_SCREEN_WIDTH = 800
BASE_SCREEN_HEIGHT = 600

# MODIFIED: Initialize the screen in FULLSCREEN mode.
# Using (0, 0) with the FULLSCREEN flag tells Pygame to use the current desktop resolution.
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Apex Chronicles")

# --- Colors (No changes) ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
LIGHT_BLUE = (173, 216, 230)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)

# --- Game Variables (using base resolution) ---
MAX_HEALTH = 50
PUNCH_DAMAGE = 5
FIRE_FIST_DAMAGE = 10
HEALTH_REGEN_AMOUNT = 5
DEFENSE_REDUCTION_PERCENT = 0.30
BASE_GRAVITY = 1
BASE_JUMP_SPEED = -15

# --- Player Settings (using base resolution) ---
BASE_PLAYER_WIDTH = 50
BASE_PLAYER_HEIGHT = 80
BASE_PLAYER_SPEED = 5
BASE_GROUND_LEVEL = BASE_SCREEN_HEIGHT - 20

# --- Power-up Settings (using base resolution) ---
BASE_POWERUP_SIZE = 30
POWERUP_TYPES = ["fire_fist", "health_regen"]
POWERUP_SPAWN_INTERVAL_MIN = 10
POWERUP_SPAWN_INTERVAL_MAX = 15
POWERUP_SPAWN_HEALTH_THRESHOLD = MAX_HEALTH - 15

# --- Scaling Utility Functions ---
def get_scale_factors():
    """Returns the current scaling factors based on the fullscreen size vs. the base size."""
    current_width, current_height = screen.get_size()
    scale_x = current_width / BASE_SCREEN_WIDTH
    scale_y = current_height / BASE_SCREEN_HEIGHT
    return scale_x, scale_y

def scale_value(value, scale_factor):
    """Scales a single numeric value."""
    return value * scale_factor

def scale_font(font_path, base_size):
    """Scales a font size, ensuring it's at least 1."""
    scale_x, scale_y = get_scale_factors()
    # Scale font based on the smaller of the two scaling factors to maintain aspect ratio
    scaled_size = int(base_size * min(scale_x, scale_y))
    return pygame.font.Font(font_path, max(1, scaled_size))

# --- Fonts ---
FONT_PATH = "turok.ttf"
BASE_DEFAULT_FONT_SIZE = 35
BASE_SMALL_FONT_SIZE = 20
BASE_LARGE_FONT_SIZE = 50

# Game States
STATE_START_SCREEN = "start_screen"
STATE_HOW_TO_PLAY = "how_to_play"
STATE_GAME_PLAY = "game_play"
STATE_GAME_OVER = "game_over"

# --- Load Assets ---
try:
    BASE_PLAYER1_IMAGE = pygame.image.load("assets/img1.png").convert_alpha()
    BASE_PLAYER2_IMAGE = pygame.image.load("assets/img2.png").convert_alpha()
    BASE_FIRE_FIST_POWERUP_IMAGE = pygame.image.load("assets/fire.png").convert_alpha()
    BASE_HEALTH_REGEN_POWERUP_IMAGE = pygame.image.load("assets/heart.png").convert_alpha()
    BASE_BACKGROUND_IMAGE = pygame.image.load("assets/bg2.jpg").convert()
except pygame.error as e:
    print(f"Could not load an image: {e}. Using color fallbacks.")
    BASE_PLAYER1_IMAGE = pygame.Surface([BASE_PLAYER_WIDTH, BASE_PLAYER_HEIGHT]); BASE_PLAYER1_IMAGE.fill(BLUE)
    BASE_PLAYER2_IMAGE = pygame.Surface([BASE_PLAYER_WIDTH, BASE_PLAYER_HEIGHT]); BASE_PLAYER2_IMAGE.fill(RED)
    BASE_FIRE_FIST_POWERUP_IMAGE = pygame.Surface([BASE_POWERUP_SIZE, BASE_POWERUP_SIZE]); BASE_FIRE_FIST_POWERUP_IMAGE.fill(ORANGE)
    BASE_HEALTH_REGEN_POWERUP_IMAGE = pygame.Surface([BASE_POWERUP_SIZE, BASE_POWERUP_SIZE]); BASE_HEALTH_REGEN_POWERUP_IMAGE.fill(GREEN)
    BASE_BACKGROUND_IMAGE = None

# --- Player Class ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color, left_key, right_key, punch_key, defense_key, jump_key, platforms, base_player_image):
        super().__init__()
        self.base_rect = pygame.Rect(x, y, BASE_PLAYER_WIDTH, BASE_PLAYER_HEIGHT)
        self.base_image = base_player_image
        self.original_image = self.base_image.copy()
        self.color = color
        self.left_key, self.right_key, self.punch_key, self.defense_key, self.jump_key = left_key, right_key, punch_key, defense_key, jump_key
        self.platforms = platforms
        self.reset()
        self.rescale()

    def rescale(self):
        scale_x, scale_y = get_scale_factors()
        self.rect = pygame.Rect(
            int(self.base_rect.x * scale_x), int(self.base_rect.y * scale_y),
            int(self.base_rect.width * scale_x), int(self.base_rect.height * scale_y)
        )
        self.image = pygame.transform.scale(self.original_image, self.rect.size)
        self.player_speed = scale_value(BASE_PLAYER_SPEED, scale_x)
        self.jump_speed = scale_value(BASE_JUMP_SPEED, scale_y)
        self.gravity = scale_value(BASE_GRAVITY, scale_y)
        self.max_fall_speed = scale_value(15, scale_y)

    def apply_gravity(self):
        self.vertical_speed += self.gravity
        if self.vertical_speed > self.max_fall_speed: self.vertical_speed = self.max_fall_speed

    def update(self, platforms):
        self.apply_gravity()
        self.rect.y += self.vertical_speed
        platform_hit_list = pygame.sprite.spritecollide(self, platforms, False)
        for platform in platform_hit_list:
            if self.vertical_speed > 0 and self.rect.bottom <= platform.rect.top + self.vertical_speed:
                self.rect.bottom = platform.rect.top; self.vertical_speed = 0; self.on_ground = True
            elif self.vertical_speed < 0 and self.rect.top >= platform.rect.top + self.vertical_speed:
                if self.rect.top < platform.rect.bottom: self.rect.top = platform.rect.bottom; self.vertical_speed = 0
        scaled_ground_level = scale_value(BASE_GROUND_LEVEL, get_scale_factors()[1])
        if self.rect.bottom > scaled_ground_level:
            self.rect.bottom = scaled_ground_level; self.vertical_speed = 0; self.on_ground = True
        if self.vertical_speed != 0:
            self.on_ground = False
            for platform in platform_hit_list:
                if self.rect.colliderect(platform) and self.rect.bottom == platform.rect.top: self.on_ground = True; break

    def move(self, keys):
        original_x = self.rect.x
        if keys[self.left_key]: self.rect.x -= self.player_speed
        if keys[self.right_key]: self.rect.x += self.player_speed
        platform_hit_list = pygame.sprite.spritecollide(self, self.platforms, False)
        for platform in platform_hit_list:
            if not (self.rect.bottom <= platform.rect.top or self.rect.top >= platform.rect.bottom):
                if self.rect.x > original_x: self.rect.right = platform.rect.left
                elif self.rect.x < original_x: self.rect.left = platform.rect.right
        current_width, _ = screen.get_size()
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > current_width: self.rect.right = current_width

    def jump(self):
        if self.on_ground: self.vertical_speed = self.jump_speed; self.on_ground = False

    def punch(self, current_time):
        if not self.is_punching and current_time > self.punch_timer:
            self.is_punching = True; self.punch_timer = current_time + self.punch_cooldown; return True
        return False

    def defend(self, current_time):
        if not self.is_defending:
            self.is_defending = True; self.defense_timer = current_time + self.defense_duration; self.update_visual_state(current_time)

    def update_visual_state(self, current_time):
        self.original_image = self.base_image.copy()
        self.image = pygame.transform.scale(self.original_image, self.rect.size)

    def update_actions(self, current_time):
        if self.is_punching and current_time > self.punch_timer - (self.punch_cooldown * 0.7): self.is_punching = False
        if self.is_defending and current_time > self.defense_timer: self.is_defending = False
        if self.active_powerup and current_time > self.powerup_timer: self.active_powerup = None
        self.update_visual_state(current_time)

    def take_damage(self, damage):
        actual_damage = damage * (1 - DEFENSE_REDUCTION_PERCENT) if self.is_defending else damage
        self.health = max(0, self.health - actual_damage)

    def heal(self, amount):
        self.health = min(MAX_HEALTH, self.health + amount)

    def activate_powerup(self, powerup_type, current_time):
        self.active_powerup = powerup_type
        self.powerup_timer = current_time + self.powerup_duration
        if powerup_type == "health_regen": self.heal(HEALTH_REGEN_AMOUNT); self.active_powerup = None
        self.update_visual_state(current_time)

    def get_attack_damage(self):
        return FIRE_FIST_DAMAGE if self.active_powerup == "fire_fist" and time.time() < self.powerup_timer else PUNCH_DAMAGE

    def reset(self):
        self.health = MAX_HEALTH; self.is_defending = False; self.is_punching = False; self.punch_timer = 0
        self.defense_timer = 0; self.punch_cooldown = 0.5; self.defense_duration = 1.0; self.active_powerup = None
        self.powerup_duration = 5; self.powerup_timer = 0; self.vertical_speed = 0; self.on_ground = False

# --- Platform Class ---
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=BROWN):
        super().__init__(); self.base_rect = pygame.Rect(x, y, width, height); self.color = color; self.rescale()
    def rescale(self):
        scale_x, scale_y = get_scale_factors()
        self.rect = pygame.Rect(int(self.base_rect.x*scale_x), int(self.base_rect.y*scale_y), int(self.base_rect.width*scale_x), int(self.base_rect.height*scale_y))
        self.image = pygame.Surface(self.rect.size); self.image.fill(self.color)

# --- PowerUp Class ---
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, powerup_type):
        super().__init__(); self.type = powerup_type
        if self.type == "fire_fist": self.base_image = BASE_FIRE_FIST_POWERUP_IMAGE
        elif self.type == "health_regen": self.base_image = BASE_HEALTH_REGEN_POWERUP_IMAGE
        self.base_rect = pygame.Rect(0, 0, BASE_POWERUP_SIZE, BASE_POWERUP_SIZE); self.rescale()
    def rescale(self):
        scale_x, scale_y = get_scale_factors()
        self.rect = pygame.Rect(int(self.base_rect.x*scale_x), int(self.base_rect.y*scale_y), int(self.base_rect.width*scale_x), int(self.base_rect.height*scale_y))
        self.image = pygame.transform.scale(self.base_image, self.rect.size)

# --- Button Class ---
class Button:
    def __init__(self, text, x, y, width, height, color, hover_color, base_font_size, action=None):
        self.base_rect = pygame.Rect(x, y, width, height); self.text = text; self.color = color; self.hover_color = hover_color
        self.base_font_size = base_font_size; self.action = action; self.is_hovered = False; self.rescale()
    def rescale(self):
        scale_x, scale_y = get_scale_factors()
        self.rect = pygame.Rect(int(self.base_rect.x*scale_x), int(self.base_rect.y*scale_y), int(self.base_rect.width*scale_x), int(self.base_rect.height*scale_y))
        self.font = scale_font(FONT_PATH, self.base_font_size)
    def draw(self, surface):
        current_color = self.hover_color if self.is_hovered else self.color; pygame.draw.rect(surface, current_color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2); text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center); surface.blit(text_surf, text_rect)
    def check_hover(self, mouse_pos): self.is_hovered = self.rect.collidepoint(mouse_pos)
    def click(self):
        if self.action: return self.action

# --- Game Functions ---
def draw_text(text, base_font_size, color, surface, x, y, center=True):
    font = scale_font(FONT_PATH, base_font_size); scale_x, scale_y = get_scale_factors()
    scaled_x, scaled_y = int(x * scale_x), int(y * scale_y); textobj = font.render(text, True, color)
    textrect = textobj.get_rect(); textrect.center = (scaled_x, scaled_y) if center else (scaled_x, scaled_y)
    surface.blit(textobj, textrect)

def get_platform_definitions():
    return [
        (0, BASE_SCREEN_HEIGHT - 20, BASE_SCREEN_WIDTH, 20), (100, 500, 150, 20), (BASE_SCREEN_WIDTH - 250, 500, 150, 20),
        (300, 400, 200, 20), (50, 300, 100, 20), (BASE_SCREEN_WIDTH - 150, 300, 100, 20), (200, 200, 150, 20),
        (BASE_SCREEN_WIDTH - 350, 200, 150, 20), (BASE_SCREEN_WIDTH/2 - 75, 100, 150, 20), (0, 400, 80, 20), (BASE_SCREEN_WIDTH - 80, 400, 80, 20)
    ]

def game_loop():
    global game_state, last_powerup_type, powerup_spawn_timer, powerups_enabled
    platform_defs = get_platform_definitions(); platforms = pygame.sprite.Group()
    for p_def in platform_defs: platforms.add(Platform(*p_def, color=GRAY if p_def[1] == BASE_SCREEN_HEIGHT-20 else BROWN))
    player1 = Player(100, 150, BLUE, pygame.K_a, pygame.K_d, pygame.K_s, pygame.K_w, pygame.K_z, platforms, BASE_PLAYER1_IMAGE)
    player2 = Player(BASE_SCREEN_WIDTH - 100 - BASE_PLAYER_WIDTH, 150, RED, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_UP, pygame.K_RSHIFT, platforms, BASE_PLAYER2_IMAGE)
    start_platform_p1 = platforms.sprites()[6]; start_platform_p2 = platforms.sprites()[7]
    player1.base_rect.bottom = start_platform_p1.base_rect.top; player1.base_rect.centerx = start_platform_p1.base_rect.centerx; player1.on_ground = True
    player2.base_rect.bottom = start_platform_p2.base_rect.top; player2.base_rect.centerx = start_platform_p2.base_rect.centerx; player2.on_ground = True
    player1.rescale(); player2.rescale()
    players_group = pygame.sprite.Group(player1, player2); powerups_group = pygame.sprite.Group()
    clock = pygame.time.Clock(); running = True; game_over_winner = None
    try: pygame.mixer.music.load("music.mp3"); pygame.mixer.music.set_volume(0.5); pygame.mixer.music.play(-1)
    except pygame.error as e: print(f"Could not load music: {e}")
    powerups_enabled = False; last_powerup_type = None; powerup_spawn_timer = time.time() + random.uniform(POWERUP_SPAWN_INTERVAL_MIN, POWERUP_SPAWN_INTERVAL_MAX)
    while running:
        current_time = time.time(); keys = pygame.key.get_pressed(); scale_x, scale_y = get_scale_factors()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: pygame.mixer.music.stop(); game_state = STATE_START_SCREEN; return
                if event.key == player1.punch_key and player1.punch(current_time):
                    punch_offset, punch_reach = scale_value(5, scale_x), scale_value(25, scale_x); is_right = player1.rect.centerx < player2.rect.centerx
                    punch_rect = pygame.Rect(player1.rect.right+punch_offset if is_right else player1.rect.left-punch_offset-punch_reach, player1.rect.top+10*scale_y, punch_reach, player1.rect.height-20*scale_y)
                    if punch_rect.colliderect(player2.rect): player2.take_damage(player1.get_attack_damage())
                elif event.key == player1.defense_key: player1.defend(current_time)
                elif event.key == player1.jump_key: player1.jump()
                if event.key == player2.punch_key and player2.punch(current_time):
                    punch_offset, punch_reach = scale_value(5, scale_x), scale_value(25, scale_x); is_right = player2.rect.centerx < player1.rect.centerx
                    punch_rect = pygame.Rect(player2.rect.right+punch_offset if is_right else player2.rect.left-punch_offset-punch_reach, player2.rect.top+10*scale_y, punch_reach, player2.rect.height-20*scale_y)
                    if punch_rect.colliderect(player1.rect): player1.take_damage(player2.get_attack_damage())
                elif event.key == player2.defense_key: player2.defend(current_time)
                elif event.key == player2.jump_key: player2.jump()
        player1.move(keys); player2.move(keys); players_group.update(platforms); player1.update_actions(current_time); player2.update_actions(current_time)
        if not powerups_enabled and (player1.health <= POWERUP_SPAWN_HEALTH_THRESHOLD or player2.health <= POWERUP_SPAWN_HEALTH_THRESHOLD):
            powerups_enabled = True; powerup_spawn_timer = current_time + random.uniform(POWERUP_SPAWN_INTERVAL_MIN, POWERUP_SPAWN_INTERVAL_MAX)
        if powerups_enabled and current_time >= powerup_spawn_timer:
            new_powerup = PowerUp(random.choice([pt for pt in POWERUP_TYPES if pt != last_powerup_type] or POWERUP_TYPES))
            spawn_plat = random.choice([p for p in platforms.sprites() if p.base_rect.y < BASE_SCREEN_HEIGHT - 40] or platforms.sprites())
            new_powerup.base_rect.centerx = spawn_plat.base_rect.centerx; new_powerup.base_rect.bottom = spawn_plat.base_rect.top - 5
            new_powerup.rescale(); powerups_group.add(new_powerup); last_powerup_type = new_powerup.type
            powerup_spawn_timer = current_time + random.uniform(POWERUP_SPAWN_INTERVAL_MIN, POWERUP_SPAWN_INTERVAL_MAX)
        for player in players_group:
            for powerup in pygame.sprite.spritecollide(player, powerups_group, True): player.activate_powerup(powerup.type, current_time)
        if player1.health <= 0: game_over_winner, running = "Player 2 won", False
        elif player2.health <= 0: game_over_winner, running = "Player 1 won", False
        if BASE_BACKGROUND_IMAGE: screen.blit(pygame.transform.scale(BASE_BACKGROUND_IMAGE, screen.get_size()), (0, 0))
        else: screen.fill(LIGHT_BLUE)
        platforms.draw(screen); powerups_group.draw(screen); players_group.draw(screen)
        hb_x, hb_y, hb_h, hb_w = 10*scale_x, 10*scale_y, 20*scale_y, (MAX_HEALTH*3)*scale_x
        p1_health_w = (player1.health * 3) * scale_x; pygame.draw.rect(screen, RED, (hb_x, hb_y, hb_w, hb_h)); pygame.draw.rect(screen, GREEN, (hb_x, hb_y, p1_health_w, hb_h))
        draw_text(f"P1: {int(player1.health)}", BASE_SMALL_FONT_SIZE, BLACK, screen, 10 + (MAX_HEALTH*3)/2, 20)
        p2_hb_x = (BASE_SCREEN_WIDTH-10-(MAX_HEALTH*3))*scale_x; p2_health_w = (player2.health*3)*scale_x
        p2_green_bar_x = (BASE_SCREEN_WIDTH-10)*scale_x - p2_health_w; pygame.draw.rect(screen, RED, (p2_hb_x, hb_y, hb_w, hb_h)); pygame.draw.rect(screen, GREEN, (p2_green_bar_x, hb_y, p2_health_w, hb_h))
        draw_text(f"P2: {int(player2.health)}", BASE_SMALL_FONT_SIZE, BLACK, screen, BASE_SCREEN_WIDTH-10-(MAX_HEALTH*3)/2, 20)
        if player1.active_powerup == "fire_fist" and time.time() < player1.powerup_timer: draw_text("P1: Fire Fist!", BASE_SMALL_FONT_SIZE, ORANGE, screen, 10, 40, center=False)
        if player2.active_powerup == "fire_fist" and time.time() < player2.powerup_timer:
            font = scale_font(FONT_PATH, BASE_SMALL_FONT_SIZE); text_w, _ = font.size("P2: Fire Fist!")
            draw_text("P2: Fire Fist!", BASE_SMALL_FONT_SIZE, ORANGE, screen, (BASE_SCREEN_WIDTH * scale_x - text_w - 10*scale_x)/scale_x, 40, center=False)
        pygame.display.flip(); clock.tick(60)
    pygame.mixer.music.stop()
    if game_over_winner: global last_winner; last_winner = game_over_winner; game_state = STATE_GAME_OVER

def create_menu_buttons(defs): return [Button(*d) for d in defs]

def menu_loop(draw_function, buttons):
    global screen; running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in buttons:
                    if button.is_hovered: return button.click()
            if draw_function.__name__ == 'draw_how_to_play_content' and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4: draw_function(scroll_dir=-1)
                if event.button == 5: draw_function(scroll_dir=1)
        draw_function()
        for button in buttons: button.check_hover(mouse_pos); button.draw(screen)
        pygame.display.flip()

def start_screen():
    global game_state
    buttons = create_menu_buttons([("Start Game", BASE_SCREEN_WIDTH/2-100, 250, 200, 50, GREEN, YELLOW, BASE_DEFAULT_FONT_SIZE, "start"),
                                   ("Info", BASE_SCREEN_WIDTH/2-100, 320, 200, 50, BLUE, LIGHT_BLUE, BASE_DEFAULT_FONT_SIZE, "how_to_play"),
                                   ("Exit", BASE_SCREEN_WIDTH/2-100, 390, 200, 50, RED, ORANGE, BASE_DEFAULT_FONT_SIZE, "exit")])
    def draw_start_content():
        if BASE_BACKGROUND_IMAGE: screen.blit(pygame.transform.scale(BASE_BACKGROUND_IMAGE, screen.get_size()), (0, 0))
        else: screen.fill(BLACK)
        draw_text("Apex Chronicles", BASE_LARGE_FONT_SIZE, WHITE, screen, BASE_SCREEN_WIDTH/2, 150)
    action = menu_loop(draw_start_content, buttons)
    if action == "start": game_state = STATE_GAME_PLAY
    elif action == "how_to_play": game_state = STATE_HOW_TO_PLAY
    elif action == "exit": pygame.quit(); exit()

scroll_offset = 0
def how_to_play_screen():
    global game_state, scroll_offset; scroll_offset = 0
    buttons = create_menu_buttons([("Back", BASE_SCREEN_WIDTH/2-75, BASE_SCREEN_HEIGHT-70, 150, 50, GRAY, WHITE, BASE_DEFAULT_FONT_SIZE, "back")])
    controls = [("This game is made by Nesar ,Ojus ,Nischit ,Nilesh ,Nimith and Fahad", BASE_SMALL_FONT_SIZE, LIGHT_BLUE), ("--- How to Play ---", BASE_DEFAULT_FONT_SIZE, YELLOW),
        ("Objective: Reduce your opponent's health to zero!", BASE_SMALL_FONT_SIZE, WHITE), ("Player 1(Left):", BASE_SMALL_FONT_SIZE, BLUE), ("  Move Left: A", BASE_SMALL_FONT_SIZE, WHITE),
        ("  Move Right: D", BASE_SMALL_FONT_SIZE, WHITE), ("  Punch: S (Default: 5 Dmg)", BASE_SMALL_FONT_SIZE, WHITE), ("  Defend: W (Reduces Dmg by 30%)", BASE_SMALL_FONT_SIZE, WHITE),
        ("  Jump: Z", BASE_SMALL_FONT_SIZE, WHITE),  ("Player 2(Right):", BASE_SMALL_FONT_SIZE, RED), ("  Move Left: Left Arrow", BASE_SMALL_FONT_SIZE, WHITE),
        ("  Move Right: Right Arrow", BASE_SMALL_FONT_SIZE, WHITE), ("  Punch: Down Arrow (Default: 5 Dmg)", BASE_SMALL_FONT_SIZE, WHITE), ("  Defend: Up Arrow (Reduces Dmg by 30%)", BASE_SMALL_FONT_SIZE, WHITE),
        ("  Jump: Right Shift", BASE_SMALL_FONT_SIZE, WHITE),  ("Power-ups:", BASE_DEFAULT_FONT_SIZE, YELLOW),
        ("  Spawn after one player's health is 35 or less.", BASE_SMALL_FONT_SIZE, WHITE), ("  Appear on platforms (10-15s interval).", BASE_SMALL_FONT_SIZE, WHITE),
        ("  Fire Fist (Orange Orb): Punch deals 10 damage (5s duration).", BASE_SMALL_FONT_SIZE, ORANGE), ("  Health Regen (Green Orb): Instantly heals 5 health.", BASE_SMALL_FONT_SIZE, GREEN),
        ("Max Health: 50", BASE_SMALL_FONT_SIZE, WHITE), ("Press ESC during gameplay to return to Main Menu.", BASE_SMALL_FONT_SIZE, WHITE)]
    def draw_how_to_play_content(scroll_dir=0):
        global scroll_offset; scroll_offset = min(max(0, len(controls)-15), max(0, scroll_offset + scroll_dir))
        if BASE_BACKGROUND_IMAGE: screen.blit(pygame.transform.scale(BASE_BACKGROUND_IMAGE, screen.get_size()), (0, 0))
        else: screen.fill(BLACK)
        current_y, line_height = 20, 22
        for i in range(scroll_offset, len(controls)):
            line, size, color = controls[i]; draw_text(line, size, color, screen, BASE_SCREEN_WIDTH/2, current_y); current_y += line_height
    if menu_loop(draw_how_to_play_content, buttons) == "back": game_state = STATE_START_SCREEN

def game_over_screen():
    global game_state, last_winner
    buttons = create_menu_buttons([("Main Menu", BASE_SCREEN_WIDTH/2-125, 350, 250, 50, GREEN, YELLOW, BASE_DEFAULT_FONT_SIZE, "start_screen"),
                                   ("Exit Game", BASE_SCREEN_WIDTH/2-125, 420, 250, 50, RED, ORANGE, BASE_DEFAULT_FONT_SIZE, "exit")])
    def draw_game_over_content():
        if BASE_BACKGROUND_IMAGE: screen.blit(pygame.transform.scale(BASE_BACKGROUND_IMAGE, screen.get_size()), (0, 0))
        else: screen.fill(BLACK)
        draw_text("GAME OVER", BASE_LARGE_FONT_SIZE, WHITE, screen, BASE_SCREEN_WIDTH/2, 150)
        if last_winner: draw_text(last_winner, BASE_DEFAULT_FONT_SIZE, {"Player 1": BLUE, "Player 2": RED}.get(last_winner.split()[0], GREEN), screen, BASE_SCREEN_WIDTH/2, 250)
    action = menu_loop(draw_game_over_content, buttons)
    if action == "start_screen": game_state = STATE_START_SCREEN
    elif action == "exit": pygame.quit(); exit()

# --- Main Program Flow ---
game_state = STATE_START_SCREEN
last_winner = None
while True:
    pygame.mixer.music.stop()
    if game_state == STATE_START_SCREEN: start_screen()
    elif game_state == STATE_HOW_TO_PLAY: how_to_play_screen()
    elif game_state == STATE_GAME_PLAY: game_loop()
    elif game_state == STATE_GAME_OVER: game_over_screen()
