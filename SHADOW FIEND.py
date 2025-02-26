import pygame
import math
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shadow Fiend Simulator (Squares)")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class Effect:
    def __init__(self, pos, duration, damage, radius=5, is_line=False, end_pos=None):
        self.pos = pos
        self.duration = duration
        self.damage = damage
        self.current_time = 0
        self.radius = radius
        self.is_line = is_line
        self.end_pos = end_pos

    def draw(self):
        if self.is_line:
            pygame.draw.line(screen, RED, self.pos, self.end_pos, 5)
        else:
            pygame.draw.circle(screen, RED, self.pos, self.radius)

    def update(self):
        self.current_time += 1
        return self.current_time >= self.duration

class ShadowFiend(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.size = 30  
        self.color = GREEN
        self.rect = pygame.Rect(x - self.size // 2, y - self.size // 2, self.size, self.size)
        self.speed = 4  
        self.target = None
        self.souls = 0
        self.health = 100
        self.attack_cooldown = 0
        self.attack_damage = 10
        self.souls_per_kill = 1
        self.max_souls = 30
        self.effects = []

    def update(self):
        if self.target:
            dx = self.target[0] - self.rect.centerx
            dy = self.target[1] - self.rect.centery
            dist = math.hypot(dx, dy)
            if dist > 5:
                angle = math.atan2(dy, dx)
                self.rect.centerx += self.speed * math.cos(angle)
                self.rect.centery += self.speed * math.sin(angle)
            else:
                self.target = None

        for i in range(len(self.effects) - 1, -1, -1):
            effect = self.effects[i]
            if effect.update():
                self.effects.pop(i)

    def basic_attack(self, target):
        if self.attack_cooldown <= 0:
            target.health -= self.attack_damage
            self.attack_cooldown = 30 

    def requiem_of_souls(self, enemies):
        if self.souls >= 20:
            self.souls -= 20
            for enemy in enemies:
                dist = math.hypot(enemy.rect.centerx - self.rect.centerx, enemy.rect.centery - self.rect.centery)
                if dist < 150:
                    enemy.health -= 30

    def _create_raze_effect(self, dist, mouse_pos):
        dx = mouse_pos[0] - self.rect.centerx
        dy = mouse_pos[1] - self.rect.centery

        angle = math.atan2(dy, dx)

        ray_len = dist

        ray_end_x = self.rect.centerx + ray_len * math.cos(angle)
        ray_end_y = self.rect.centery + ray_len * math.sin(angle)

        effect_pos = (int(ray_end_x), int(ray_end_y))

        self.effects.append(Effect(effect_pos, 20, 20, 10))

        return effect_pos

    def shadow_raze(self, dist, mouse_pos):
        effect_pos = self._create_raze_effect(dist, mouse_pos)

        for enemy in enemies:
            dist_to_enemy = math.hypot(
                effect_pos[0] - enemy.rect.centerx, effect_pos[1] - enemy.rect.centery
            )
            if dist_to_enemy <= 30:
                enemy.health -= 20

    def shadow_raze_around(self):
        for angle in range(0, 360, 45):
            angle_rad = math.radians(angle)
            ray_len = 500

            ray_end_x = self.rect.centerx + ray_len * math.cos(angle_rad)
            ray_end_y = self.rect.centery + ray_len * math.sin(angle_rad)

            self.effects.append(Effect(self.rect.center, 20, 20, is_line=True, end_pos=(ray_end_x, ray_end_y)))

            for enemy in enemies:
                enemy_rect_points = [
                    enemy.rect.topleft,
                    enemy.rect.topright,
                    enemy.rect.bottomright,
                    enemy.rect.bottomleft,
                ]
                for point in enemy_rect_points:
                    dist_to_enemy = math.hypot(point[0] - self.rect.centerx, point[1] - self.rect.centery)
                    if dist_to_enemy <= ray_len:
                        enemy.health -= 20


class Creep(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.size = 20
        self.color = BLUE
        self.rect = pygame.Rect(x - self.size // 2, y - self.size // 2, self.size, self.size)
        self.speed = 1.5
        self.health = 30
        self.attack_cooldown = 0
        self.attack_damage = 5

    def update(self, target):
        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery

        angle = math.atan2(dy, dx)

        self.rect.centerx += self.speed * math.cos(angle)
        self.rect.centery += self.speed * math.sin(angle)

        dist = math.hypot(dx, dy)
        if dist < 45:
            self.basic_attack(target)

    def basic_attack(self, target):
        if self.attack_cooldown <= 0:
            target.health -= self.attack_damage
            self.attack_cooldown = 30

all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()

sf = ShadowFiend(WIDTH // 2, HEIGHT // 2)
all_sprites.add(sf)

for _ in range(5):
    x = random.randint(50, WIDTH - 50)
    y = random.randint(50, HEIGHT - 50)
    creep = Creep(x, y)
    all_sprites.add(creep)
    enemies.add(creep)

creep_spawn_timer = 0
creep_spawn_interval = 2000  

running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3: 
                sf.target = event.pos

        if event.type == pygame.KEYDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if event.key == pygame.K_q:
                sf.shadow_raze(50, mouse_pos)
            elif event.key == pygame.K_w:
                sf.shadow_raze(100, mouse_pos)
            elif event.key == pygame.K_e:
                sf.shadow_raze(200, mouse_pos)
            elif event.key == pygame.K_r:
                sf.shadow_raze_around()

    sf.update()

    for creep in enemies:
        creep.update(sf)

    if sf.attack_cooldown > 0:
        sf.attack_cooldown -= 1

    for creep in enemies:
        if creep.attack_cooldown > 0:
            creep.attack_cooldown -= 1

    for creep in enemies:
        if creep.health <= 0:
            sf.souls += sf.souls_per_kill
            if sf.souls > sf.max_souls:
                sf.souls = sf.max_souls
            enemies.remove(creep)
            all_sprites.remove(creep)

    creep_spawn_timer += clock.get_time()
    if creep_spawn_timer >= creep_spawn_interval:
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 50)
        creep = Creep(x, y)
        all_sprites.add(creep)
        enemies.add(creep)
        creep_spawn_timer = 0

    screen.fill(BLACK)
    for entity in all_sprites:
        pygame.draw.rect(screen, entity.color, entity.rect)

    for effect in sf.effects:
        effect.draw()

    font = pygame.font.Font(None, 20)
    hp_text = font.render(f"Health: {sf.health}", True, WHITE)
    screen.blit(hp_text, (10, 10))

    souls_text = font.render(f"Souls: {sf.souls}", True, WHITE)
    screen.blit(souls_text, (10, 30))

    pygame.display.flip()

    clock.tick(60)

pygame.quit()