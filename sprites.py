import pygame
from screen_vars import SCREEN_HEIGHT, SCREEN_WIDTH
import collections

class Player(pygame.sprite.Sprite):
    def __init__(self, images, bouquet_image):
        super().__init__()
        self.images = images  # Словарь с анимациями
        self.bouquet_image = bouquet_image  # Изображение букета для стрельбы
        self.scale_factor = 0.7  # Уменьшение размера на 0.7 раза от исходного
        self.image = pygame.transform.scale(self.images['idle'][0], (int(self.images['idle'][0].get_width() * self.scale_factor), int(self.images['idle'][0].get_height() * self.scale_factor)))
        self.rect = self.image.get_rect()
        self.rect.center = (100, SCREEN_HEIGHT - 117)
        self.current_animation = 'idle'
        self.animation_index = 0
        self.animation_speed = 0.1
        self.animation_timer = 0
        self.velocity_y = 0
        self.is_jumping = False
        self.facing_right = True
        self.on_ground = True
        self.bouquet_count = 0
        self.boost_count = 0  # Добавляем счетчик бустов
        self.projectiles = pygame.sprite.Group()
        self.can_shoot = True
        self.shoot_cooldown = 500  # Задержка между выстрелами в миллисекундах
        self.last_shot_time = 0
        self.boosted = False
        self.boost_end_time = 0
        self.speed = 5  # Стартовая скорость
        self.base_speed = self.speed  # Базовая скорость для восстановления
        self.dead = False  # Добавляем переменную для отслеживания состояния смерти
        self.death_animation_done = False

    def boost(self):
        self.boosted = True
        self.speed = self.base_speed * 1.5  # Увеличиваем скорость
        self.boost_end_time = pygame.time.get_ticks() + 2000  # 2 секунды буста
        self.boost_count += 1  # Увеличиваем счетчик бустов

    def update(self, keys, obstacles):
        if not self.dead:
            self.handle_input(keys)
            self.apply_gravity()
            self.check_ground()
            self.animate()
            self.check_collisions(obstacles)
            self.projectiles.update()

            if self.boosted and pygame.time.get_ticks() >= self.boost_end_time:
                self.speed = self.base_speed  # Восстанавливаем базовую скорость после окончания буста
                self.boosted = False
        else:
            self.play_death_animation()

    def play_death_animation(self):
        self.current_animation = 'death'
        self.animate()
        if self.animation_index == len(self.images['death']) - 1:
            self.death_animation_done = True

    def handle_input(self, keys):
        moving_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        moving_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        jumping = keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]
        shooting = keys[pygame.K_f]

        initial_position = SCREEN_WIDTH // 2

        if moving_left and self.rect.centerx > initial_position:
            self.current_animation = 'run'
            self.rect.x -= self.speed
            self.facing_right = False
        elif moving_left:
            self.current_animation = 'run'
            self.facing_right = False

        if moving_right and self.rect.centerx < initial_position:
            self.current_animation = 'run'
            self.rect.x += self.speed
            self.facing_right = True
        elif moving_right:
            self.current_animation = 'run'
            self.facing_right = True

        if jumping and self.on_ground:
            self.velocity_y = -20  # Увеличенная скорость прыжка для более высокой высоты
            self.is_jumping = True
            self.on_ground = False
            self.current_animation = 'jump'
        if not moving_left and not moving_right and self.on_ground:
            self.current_animation = 'idle'
            self.animation_index = 0  # Сброс анимации на первый кадр для состояния покоя

        if shooting and self.bouquet_count > 0 and self.can_shoot:
            self.shoot()

    def apply_gravity(self):
        # вот сюда написать код который будет считать если чел стоит не на платформе то пусть он падает
        # это будет фиксом бага с тем что он по воздуху ходит

        if not self.on_ground:
            self.velocity_y += 1  # Ускорение под действием гравитации
        self.rect.y += self.velocity_y

    def check_ground(self):
        ground_level = SCREEN_HEIGHT - 117
        if self.rect.bottom >= ground_level:
            self.rect.bottom = ground_level
            self.is_jumping = False
            self.on_ground = True
            self.velocity_y = 0

    def animate(self):
        if self.current_animation == 'idle':
            self.image = pygame.transform.scale(self.images['idle'][0], (int(self.images['idle'][0].get_width() * self.scale_factor), int(self.images['idle'][0].get_height() * self.scale_factor)))
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
        else:
            self.animation_timer += self.animation_speed
            if self.animation_timer >= 1:
                self.animation_timer = 0
                self.animation_index = (self.animation_index + 1) % len(self.images[self.current_animation])
                self.image = pygame.transform.scale(self.images[self.current_animation][self.animation_index], (int(self.images[self.current_animation][self.animation_index].get_width() * self.scale_factor), int(self.images[self.current_animation][self.animation_index].get_height() * self.scale_factor)))
                if not self.facing_right:
                    self.image = pygame.transform.flip(self.image, True, False)

    def check_collisions(self, obstacles):
        collisions = pygame.sprite.spritecollide(self, obstacles, False)
        ground_level = SCREEN_HEIGHT - 117

        if len(collisions) == 0 and self.rect.bottom != ground_level and not self.is_jumping:
            self.velocity_y += 10
            self.on_ground = False
        else:
            for obstacle in collisions:
                if self.velocity_y > 0:  # Падение вниз
                    self.rect.bottom = obstacle.rect.top
                    self.is_jumping = False
                    self.on_ground = True
                    self.velocity_y = 0

    def shoot(self):
        bouquet_image = self.bouquet_image  # Используем изображение букета
        projectile = Projectile(self.rect.centerx, self.rect.centery, bouquet_image, self.facing_right)
        self.projectiles.add(projectile)
        self.bouquet_count -= 1
        self.can_shoot = False
        self.last_shot_time = pygame.time.get_ticks()

    def update_shoot_cooldown(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot_time >= self.shoot_cooldown:
                self.can_shoot = True

class StationaryEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y, images):
        super().__init__()
        self.images = images  # Словарь с анимациями
        self.image = pygame.transform.scale(self.images['idle'][0], (self.images['idle'][0].get_width() // 3, self.images['idle'][0].get_height() // 3))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y - self.rect.height)  # Разместить тещу над платформой
        self.current_animation = 'idle'
        self.animation_index = 0
        self.animation_speed = 0.015  # Уменьшенная скорость анимации для врагов
        self.animation_timer = 0

    def update(self):
        self.animate()

    def animate(self):
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.animation_index = (self.animation_index + 1) % len(self.images[self.current_animation])
            self.image = pygame.transform.scale(self.images[self.current_animation][self.animation_index], (self.images[self.current_animation][self.animation_index].get_width() // 3, self.images[self.current_animation][self.animation_index].get_height() // 3))

class Boost(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.image.get_width() // 2, self.image.get_height() // 2))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.image.get_width() // 1.5, self.image.get_height() // 1.5))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, image, facing_right):
        super().__init__()
        self.image = pygame.transform.scale(image, (int(image.get_width() * 0.5), int(image.get_height() * 0.5)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10 if facing_right else -10

    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

class Bouquet(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.image.get_width() // 2, self.image.get_height() // 2))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Bride(pygame.sprite.Sprite):
    def __init__(self, images, target):
        super().__init__()
        self.images = images  # Словарь с анимациями
        self.target = target  # Жених, за которым следует невеста
        self.scale_factor = 0.7  # Уменьшение размера на 0.7 раза от исходного
        self.image = pygame.transform.scale(self.images['idle'][0], (int(self.images['idle'][0].get_width() * self.scale_factor), int(self.images['idle'][0].get_height() * self.scale_factor)))
        self.rect = self.image.get_rect()
        self.rect.center = (50, target.rect.centery)  # Невеста начинает в левом краю экрана
        self.current_animation = 'idle'
        self.animation_index = 0
        self.animation_speed = 0.1
        self.animation_timer = 0
        self.velocity_y = 0
        self.is_jumping = False
        self.facing_right = True
        self.on_ground = True
        self.base_speed = .75  # Базовая скорость невесты
        # self.speed_multiplier = 1 / 5  # Невеста движется медленнее жениха
        self.actions_queue = collections.deque(maxlen=120)  # Очередь действий жениха с увеличенной задержкой
        self.jump_delay = 30  # Увеличенная задержка прыжка невесты

    def update(self):
        self.record_actions()
        self.follow_target()
        self.animate()

    def record_actions(self):
        # Сохраняем действия жениха в очередь
        action = {
            'x': self.target.rect.x,
            'y': self.target.rect.y,
            'is_jumping': self.target.is_jumping,
            'on_ground': self.target.on_ground,
            'velocity_y': self.target.velocity_y
        }
        self.actions_queue.append(action)

    def follow_target(self):
        if len(self.actions_queue) >= self.jump_delay:
            action = self.actions_queue.popleft()

            # self.rect.x = action['x'] - 300  # Отставание по X координате, чтобы невеста не была слишком близко к жениху
            # self.facing_right = self.target.facing_right  # Направление движения невесты
            if self.target.boosted:
                self.rect.x -= (self.target.speed - self.target.base_speed) - self.base_speed
            else:
                self.rect.x += self.base_speed

            # Исправление: добавляем not для корректного прыжка
            if action['is_jumping'] and not action['on_ground']:
                self.velocity_y = action['velocity_y']
                self.is_jumping = True
                self.on_ground = False
            else:
                self.apply_gravity()

            # Держимся на платформе после прыжка
            self.rect.y = action['y']
            if action['on_ground']:
                self.on_ground = True
                self.is_jumping = False
                self.velocity_y = 0
            else:
                self.apply_gravity()

    def apply_gravity(self):
        if not self.on_ground:
            self.velocity_y += 1  # Ускорение под действием гравитации
        self.rect.y += self.velocity_y

        if self.rect.bottom >= SCREEN_HEIGHT - 117:
            self.rect.bottom = SCREEN_HEIGHT - 117
            self.is_jumping = False
            self.on_ground = True
            self.velocity_y = 0

    def animate(self):
        if self.is_jumping:
            self.current_animation = 'jump'
        elif self.facing_right:
            self.current_animation = 'run_right'
        else:
            self.current_animation = 'run_left'

        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.animation_index = (self.animation_index + 1) % len(self.images[self.current_animation])
        self.image = pygame.transform.scale(self.images[self.current_animation][self.animation_index], (int(self.images[self.current_animation][self.animation_index].get_width() * self.scale_factor), int(self.images[self.current_animation][self.animation_index].get_height() * self.scale_factor)))
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)


class ChasingEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y, images, target):
        super().__init__()
        self.images = {key: [pygame.transform.scale(img, (img.get_width() // 3, img.get_height() // 3)) for img in img_list] for key, img_list in images.items()}
        self.image = self.images['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.current_animation = 'idle'
        self.animation_index = 0
        self.animation_speed = 0.015
        self.animation_timer = 0
        self.target = target
        self.speed = 2

    def update(self):
        self.animate()
        self.chase_target()

    def animate(self):
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.animation_index = (self.animation_index + 1) % len(self.images[self.current_animation])
            self.image = self.images[self.current_animation][self.animation_index]

    def chase_target(self):
        if self.target.rect.x > self.rect.x:
            self.rect.x += self.speed
        elif self.target.rect.x < self.rect.x:
            self.rect.x -= self.speed

        if self.target.rect.y > self.rect.y:
            self.rect.y += self.speed
        elif self.target.rect.y < self.rect.y:
            self.rect.y -= self.speed

class MovingPlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path, direction='horizontal', range=100, speed=2):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.image.get_width() // 2, self.image.get_height() // 2))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.direction = direction
        self.range = range
        self.speed = speed
        self.start_pos = pygame.math.Vector2(self.rect.topleft)

    def update(self):
        if self.direction == 'horizontal':
            self.rect.x += self.speed
            if abs(self.rect.x - self.start_pos.x) > self.range:
                self.speed = -self.speed
        elif self.direction == 'vertical':
            self.rect.y += self.speed
            if abs(self.rect.y - self.start_pos.y) > self.range:
                self.speed = -self.speed