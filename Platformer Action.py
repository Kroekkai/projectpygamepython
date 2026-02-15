import pygame
import random

pygame.init()

# กำหนดค่าหน้าจอ
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# โหลดฉากหลัง
background_img = pygame.image.load("background.png")
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

def draw_text(text, x, y, color=(255, 255, 255)):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

# เมนูหลัก
def main_menu():
    cover_image = pygame.image.load("bibb.png")
    cover_image = pygame.transform.scale(cover_image, (WIDTH, HEIGHT))

    while True:
        screen.fill((0, 0, 0))
        screen.blit(cover_image, (0, 0))

        # วาดกรอบและพื้นหลังของปุ่ม
        pygame.draw.rect(screen, (100, 100, 100), (340, 240, 120, 40))
        pygame.draw.rect(screen, (100, 100, 100), (340, 290, 120, 40))
        draw_text("1. Start", 355, 250)
        draw_text("2. Exit", 355, 300)

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return
                if event.key == pygame.K_2:
                    pygame.quit()
                    exit()

# โหลดตัวละคร
player_sprites = [pygame.transform.scale(pygame.image.load(f"player{i}.png"), (125, 125)) for i in range(1, 6)]
player_jump_img = pygame.transform.scale(pygame.image.load("player_jump.png"), (125, 125)) # ภาพตอนกระโดด
player_index = 0
player_img = player_sprites[player_index]
player_rect = player_img.get_rect(midbottom=(100, 500))
player_health = 100

# โหลดศัตรู
enemy_sprites = [pygame.transform.scale(pygame.image.load(f"enemy{i}.png"), (125, 125)) for i in range(1, 3)]
enemy_img = enemy_sprites[0]
enemies = []
enemy_health = {}

# โหลดบอส
boss_img = pygame.transform.scale(pygame.image.load("boss.png"), (150, 150))
boss_rect = boss_img.get_rect(midbottom=(700, 500))
boss_health = 300
boss_alive = False

# กระสุนจากบอส
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
    
    def update(self):
        self.rect.x -= 7
        if self.rect.right < 0:
            self.kill()

bullet_group = pygame.sprite.Group()

# ระบบด่าน
current_level = 1
max_level = 3

def spawn_enemies():
    global enemies, enemy_health, boss_alive, boss_health, boss_rect
    enemies.clear()
    enemy_health.clear()
    if current_level == 3:
        boss_alive = True
        boss_health = 300
        boss_rect = boss_img.get_rect(midbottom=(700, 500))
    else:
        num_enemies = 3 + (current_level - 1) * 2
        for _ in range(num_enemies):
            enemy_rect = enemy_img.get_rect(midbottom=(random.randint(500, 800), 500))
            enemies.append(enemy_rect)
            enemy_health[id(enemy_rect)] = 50 + (current_level * 10)

# ความเร็วและแรงโน้มถ่วง
speed = 5
gravity = 1
jump_power = -15
velocity_y = 0
on_ground = False
animation_timer = 0

# ระบบอาวุธ
class Sword(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=(x, y))
    
    def update(self):
        self.rect.x += 10
        if self.rect.x > WIDTH:
            self.kill()

sword_group = pygame.sprite.Group()

# ระบบไอเท็ม
class Item(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))

item_group = pygame.sprite.Group()
for _ in range(3):
    item = Item(random.randint(100, 700), 450)
    item_group.add(item)

# เริ่มเกม
main_menu()
spawn_enemies()

# ตัวแปรยิงกระสุนบอส
boss_shoot_timer = 0
boss_shoot_cooldown = 60

# ลูปหลักของเกม
running = True
while running:
    screen.blit(background_img, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            sword = Sword(player_rect.x + 50, player_rect.y + 20)
            sword_group.add(sword)

    # การควบคุม
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_rect.x -= speed
    if keys[pygame.K_RIGHT]:
        player_rect.x += speed
    if keys[pygame.K_SPACE] and on_ground:
        velocity_y = jump_power
        on_ground = False

    # แรงโน้มถ่วง
    velocity_y += gravity
    player_rect.y += velocity_y
    if player_rect.bottom >= 500:
        player_rect.bottom = 500
        velocity_y = 0
        on_ground = True

    # ศัตรูเดินเข้าหาผู้เล่น
    for enemy in enemies[:]:
        if enemy.x > player_rect.x:
            enemy.x -= 2
        else:
            enemy.x += 2

    # ยิงกระสุนจากบอส
    if boss_alive:
        boss_shoot_timer += 1
        if boss_shoot_timer >= boss_shoot_cooldown:
            bullet = Bullet(boss_rect.centerx - 20, boss_rect.centery)
            bullet_group.add(bullet)
            boss_shoot_timer = 0

    # การชนกับศัตรู
    for enemy in enemies:
        if player_rect.colliderect(enemy):
            player_health -= 1
    if boss_alive and player_rect.colliderect(boss_rect):
        player_health -= 1


    # อัปเดตกลุ่ม
    sword_group.update()
    bullet_group.update()

    # ตรวจสอบการโจมตี
    for enemy in enemies[:]:
        for sword in sword_group:
            if enemy.colliderect(sword.rect):
                enemy_health[id(enemy)] -= 20
                sword.kill()
                if enemy_health[id(enemy)] <= 0:
                    enemies.remove(enemy)
                    del enemy_health[id(enemy)]

    if boss_alive:
        for sword in sword_group:
            if boss_rect.colliderect(sword.rect):
                boss_health -= 20
                sword.kill()
                if boss_health <= 0:
                    boss_alive = False

    # ตรวจสอบการโดนกระสุน
    for bullet in bullet_group:
        if player_rect.colliderect(bullet.rect):
            player_health -= 10
            bullet.kill()

    # ตรวจสอบการเก็บไอเท็ม
    for item in item_group:
        if player_rect.colliderect(item.rect):
            item.kill()
            player_health += 10

    # ตรวจสอบตาย
    if player_health <= 0:
        screen.fill((0, 0, 0))
        draw_text("Game Over", 350, 250, (255, 0, 0))
        pygame.display.update()
        pygame.time.delay(2000)
        main_menu()
        player_health = 100
        current_level = 1
        spawn_enemies()

    if not enemies and not boss_alive:
        if current_level < max_level:
            current_level += 1
            spawn_enemies()
        else:
            screen.fill((0, 0, 0))
            draw_text("Win!", 350, 250, (0, 255, 0))
            pygame.display.update()
            pygame.time.delay(3000)
            main_menu()
            player_health = 100
            current_level = 1
            spawn_enemies()
   
    # อนิเมชั่นตัวละคร
    if not on_ground:
        player_img = player_jump_img
    else:
        animation_timer += 1
        if animation_timer >= 10:
            player_index = (player_index + 1) % len(player_sprites)
            player_img = player_sprites[player_index]
            animation_timer = 0

    # วาดวัตถุ
    screen.blit(player_img, player_rect)
    for enemy in enemies:
        screen.blit(enemy_img, enemy)
        pygame.draw.rect(screen, (255, 0, 0), (enemy.x, enemy.y - 10, enemy_health[id(enemy)], 5))

    item_group.draw(screen)
    sword_group.draw(screen)
    bullet_group.draw(screen)

    if boss_alive:
        screen.blit(boss_img, boss_rect)
        pygame.draw.rect(screen, (255, 0, 0), (boss_rect.x, boss_rect.y - 20, boss_health, 10))

    pygame.draw.rect(screen, (255, 0, 0), (20, 20, player_health * 2, 10))  # HP

    pygame.display.update()
    clock.tick(60)

pygame.quit()
