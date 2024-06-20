import pygame
from sprites import (
    Player,
    Obstacle,
    Bouquet,
    ChasingEnemy,
    Bride,
    Boost,
    StationaryEnemy,
    MovingPlatform,
)
from screen_vars import SCREEN_WIDTH, SCREEN_HEIGHT
import random

class Level:
    def __init__(self, player_images, enemy_images, bouquet_image, background_images):
        self.player = Player(player_images, bouquet_image)
        self.obstacles = pygame.sprite.Group()
        self.bouquets = pygame.sprite.Group()  # Группа для букетов
        self.boosts = pygame.sprite.Group()  # Группа для бустов
        self.enemies = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.player_images = player_images
        self.enemy_images = enemy_images
        self.background_images = [pygame.transform.scale(pygame.image.load(img), (SCREEN_WIDTH, SCREEN_HEIGHT)) for img in background_images]
        self.background_x = 0
        self.scroll_speed = 5  # Скорость прокрутки

        # Инициализация позиции жениха в центре экрана
        self.player.rect.centerx = SCREEN_WIDTH // 2
        self.player_start_x = self.player.rect.x

        self.score = 0  # Начальный счет
        self.bouquet_count = 0  # Количество собранных букетов

    def update(self, keys):
        self.player.update(keys, self.obstacles)  # Передаем препятствия в метод update игрока
        self.scroll_background(keys)
        self.obstacles.update()
        self.bouquets.update()
        self.boosts.update()
        self.enemies.update()
        self.player.projectiles.update()
        self.check_bouquet_collisions()
        self.check_boost_collisions()
        self.player.update_shoot_cooldown()  # Обновляем состояние стрельбы
        self.check_enemy_collisions()  # Новая проверка на уничтожение врагов

        if self.player.death_animation_done:
            return 'lose'

        if pygame.sprite.collide_rect(self.player, self.bride):
            self.player.dead = True

        if self.score >= 100:
            return 'win'
        return None

    def draw(self, screen):
        for i, bg in enumerate(self.background_images):
            screen.blit(bg, (self.background_x + i * SCREEN_WIDTH, 0))
            screen.blit(bg, (self.background_x + (i - 1) * SCREEN_WIDTH, 0))
            screen.blit(bg, (self.background_x + (i + 1) * SCREEN_WIDTH, 0))

        for obstacle in self.obstacles:
            screen.blit(obstacle.image, obstacle.rect)
        self.bouquets.draw(screen)
        self.boosts.draw(screen)
        self.player.projectiles.draw(screen)
        self.all_sprites.draw(screen)

        font = pygame.font.SysFont(None, 55)
        score_text = font.render(f'Score: {self.score}', True, (0, 0, 128))
        screen.blit(score_text, (10, SCREEN_HEIGHT - 70))

        bouquet_image = pygame.image.load('images/bonus/flowers/flowers0.png').convert_alpha()
        screen.blit(bouquet_image, (10, SCREEN_HEIGHT - 130))
        bouquet_count_text = font.render(f'{self.player.bouquet_count}', True, (0, 0, 128))
        screen.blit(bouquet_count_text, (60, SCREEN_HEIGHT - 130))

        boost_image = pygame.image.load('images/boost/rings/rings0.png').convert_alpha()
        screen.blit(boost_image, (10, SCREEN_HEIGHT - 190))
        boost_count_text = font.render(f'{self.player.boost_count}', True, (0, 0, 128))
        screen.blit(boost_count_text, (60, SCREEN_HEIGHT - 190))

    def scroll_background(self, keys):
        player_moving_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        player_moving_left = keys[pygame.K_LEFT] or keys[pygame.K_a]

        scroll_speed = self.player.speed  # Используем текущую скорость игрока для прокрутки

        if player_moving_right:
            self.background_x -= scroll_speed
            for obstacle in self.obstacles:
                obstacle.rect.x -= scroll_speed
            for bouquet in self.bouquets:
                bouquet.rect.x -= scroll_speed
            for boost in self.boosts:
                boost.rect.x -= scroll_speed
            for enemy in self.enemies:
                enemy.rect.x -= scroll_speed

        if player_moving_left and self.background_x < 0:  # Ограничиваем движение влево
            self.background_x += scroll_speed
            for obstacle in self.obstacles:
                obstacle.rect.x += scroll_speed
            for bouquet in self.bouquets:
                bouquet.rect.x += scroll_speed
            for boost in self.boosts:
                boost.rect.x += scroll_speed
            for enemy in self.enemies:
                enemy.rect.x += scroll_speed

        if self.background_x <= -SCREEN_WIDTH:
            self.background_x = 0
            self.background_images.append(self.background_images.pop(0))
        elif self.background_x >= SCREEN_WIDTH:
            self.background_x = 0
            self.background_images.insert(0, self.background_images.pop())

        # Жених остается в центре экрана независимо от направления движения
        self.player.rect.centerx = SCREEN_WIDTH // 2

    def check_bouquet_collisions(self):
        # Проверка столкновений с букетами
        collided_bouquets = pygame.sprite.spritecollide(self.player, self.bouquets, True)
        for bouquet in collided_bouquets:
            self.score += 10  # Пример добавления очков за сбор букета
            self.player.bouquet_count += 1  # Увеличиваем количество собранных букетов

    def check_boost_collisions(self):
        # Проверка столкновений с бустами
        collided_boosts = pygame.sprite.spritecollide(self.player, self.boosts, True)
        for boost in collided_boosts:
            self.player.boost()

    def check_collisions(self):
        # Проверка столкновений с препятствиями
        if pygame.sprite.spritecollideany(self.player, self.obstacles):
            self.player.rect.y = SCREEN_HEIGHT - 117  # Возвращаем на землю

        # Проверка столкновений с врагами
        if pygame.sprite.spritecollideany(self.player, self.enemies):
            self.player.rect.x = self.player_start_x  # Возвращаем в начало уровня

    def check_enemy_collisions(self):
        for projectile in self.player.projectiles:
            enemy_hit = pygame.sprite.spritecollideany(projectile, self.enemies)
            if enemy_hit:
                enemy_hit.kill()
                projectile.kill()
                self.score += 10  # Пример добавления очков за уничтожение врага

class Level1(Level):
    def __init__(self, player_images, enemy_images, bride_images):
        background_images = [
            "images/level1/background-1.png",
            "images/level1/background-2.png",
            "images/level1/background-3.png"
        ]
        bouquet_image = pygame.image.load("images/bonus/flowers/flowers0.png").convert_alpha()  # Изображение букета
        super().__init__(player_images, enemy_images, bouquet_image, background_images)

        platform_positions = [
            (SCREEN_WIDTH + 55, SCREEN_HEIGHT - 300),
            (SCREEN_WIDTH + 400, SCREEN_HEIGHT - 350),
            (SCREEN_WIDTH + 725, SCREEN_HEIGHT - 400),
            (SCREEN_WIDTH + 1050, SCREEN_HEIGHT - 300),
            (SCREEN_WIDTH + 1375, SCREEN_HEIGHT - 350),
            (SCREEN_WIDTH + 1700, SCREEN_HEIGHT - 300),
            (SCREEN_WIDTH + 2025, SCREEN_HEIGHT - 350),
            (SCREEN_WIDTH + 2350, SCREEN_HEIGHT - 400),
            (SCREEN_WIDTH + 2675, SCREEN_HEIGHT - 300),
            (SCREEN_WIDTH + 3000, SCREEN_HEIGHT - 350),
            (SCREEN_WIDTH + 3325, SCREEN_HEIGHT - 400),
            (SCREEN_WIDTH + 3650, SCREEN_HEIGHT - 300),
            (SCREEN_WIDTH + 3975, SCREEN_HEIGHT - 350),
            (SCREEN_WIDTH + 4300, SCREEN_HEIGHT - 400),
            (SCREEN_WIDTH + 4625, SCREEN_HEIGHT - 300),
            (SCREEN_WIDTH + 4950, SCREEN_HEIGHT - 350),
            (SCREEN_WIDTH + 5275, SCREEN_HEIGHT - 400),
            (SCREEN_WIDTH + 5600, SCREEN_HEIGHT - 300),
            (SCREEN_WIDTH + 5925, SCREEN_HEIGHT - 350),
            (SCREEN_WIDTH + 6250, SCREEN_HEIGHT - 300),
            (SCREEN_WIDTH + 6575, SCREEN_HEIGHT - 350),
            (SCREEN_WIDTH + 6900, SCREEN_HEIGHT - 400),
            (SCREEN_WIDTH + 7225, SCREEN_HEIGHT - 300),
            (SCREEN_WIDTH + 7550, SCREEN_HEIGHT - 350),
            (SCREEN_WIDTH + 7875, SCREEN_HEIGHT - 400)
        ]
        platform_images = [
            "images/level1/platform-1.png",
            "images/level1/platform-2.png",
            "images/level1/platform-3.png",
            "images/level1/platform-4.png",
            "images/level1/platform-5.png",
            "images/level1/platform-6.png",
            "images/level1/platform-7.png",
            "images/level1/platform-8.png",
            "images/level1/platform-9.png",
            "images/level1/platform-10.png",
            "images/level1/platform-11.png",
            "images/level1/platform-12.png",
            "images/level1/platform-13.png",
            "images/level1/platform-14.png"
        ] * 2  # Увеличиваем количество платформ в два раза

        bouquet_positions = [
            (SCREEN_WIDTH + 55, SCREEN_HEIGHT - 390),
            (SCREEN_WIDTH + 725, SCREEN_HEIGHT - 490),
            (SCREEN_WIDTH + 1700, SCREEN_HEIGHT - 390),
            (SCREEN_WIDTH + 2025, SCREEN_HEIGHT - 390),
            (SCREEN_WIDTH + 3000, SCREEN_HEIGHT - 440),
            (SCREEN_WIDTH + 3650, SCREEN_HEIGHT - 390),
            (SCREEN_WIDTH + 4300, SCREEN_HEIGHT - 490),
            (SCREEN_WIDTH + 4950, SCREEN_HEIGHT - 490),
            (SCREEN_WIDTH + 5600, SCREEN_HEIGHT - 440),
            (SCREEN_WIDTH + 6250, SCREEN_HEIGHT - 390),
            (SCREEN_WIDTH + 6900, SCREEN_HEIGHT - 440),
            (SCREEN_WIDTH + 7550, SCREEN_HEIGHT - 390)
        ]
        bouquet_images = [
            'images/bonus/flowers/flowers0.png',
            'images/bonus/flowers/flowers1.png',
            'images/bonus/flowers/flowers2.png'
        ]
        enemy_positions = [
            (SCREEN_WIDTH + 730, SCREEN_HEIGHT - 390),
            (SCREEN_WIDTH + 2025, SCREEN_HEIGHT - 350),
            (SCREEN_WIDTH + 5600, SCREEN_HEIGHT - 390),
        ]
        boost_positions = [
            (SCREEN_WIDTH + 500, SCREEN_HEIGHT - 400),
            (SCREEN_WIDTH + 2500, SCREEN_HEIGHT - 450),
            (SCREEN_WIDTH + 4500, SCREEN_HEIGHT - 400),
            (SCREEN_WIDTH + 6500, SCREEN_HEIGHT - 450)
        ]
        venus_flytrap_positions = [
            (SCREEN_WIDTH + 1000, SCREEN_HEIGHT - 217),
            (SCREEN_WIDTH + 3200, SCREEN_HEIGHT - 217),
            (SCREEN_WIDTH + 6000, SCREEN_HEIGHT - 217)
        ]
        
        # Добавление препятствий
        for pos, img in zip(platform_positions, platform_images):
            obstacle = Obstacle(pos[0], pos[1], img)
            self.obstacles.add(obstacle)
            self.all_sprites.add(obstacle)
        
        # Добавление букетов
        for k, (x, y) in enumerate(bouquet_positions):
            image = bouquet_images[k % len(bouquet_images)]
            bouquet = Bouquet(x, y, image)
            self.bouquets.add(bouquet)
            self.all_sprites.add(bouquet)

        # Добавление бустов
        for (x, y) in boost_positions:
            boost = Boost(x, y, "images/boost/rings/rings0.png")
            self.boosts.add(boost)
            self.all_sprites.add(boost)

        # Добавление врагов
        for pos in enemy_positions:
            enemy = StationaryEnemy(pos[0], pos[1], enemy_images['teshya'])
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

        # Добавление Venus Flytraps
        for (x, y) in venus_flytrap_positions:
            venus_flytrap = Obstacle(x, y, "images/obstacles/venus-flytrap/venusflytrap.png")
            self.obstacles.add(venus_flytrap)
            self.all_sprites.add(venus_flytrap)

        # Добавление невесты
        self.bride = Bride(bride_images, self.player)
        self.all_sprites.add(self.bride)

    def update(self, keys):
        self.player.update(keys, self.obstacles)
        self.bride.update()  # Обновляем невесту
        self.scroll_background(keys)
        self.obstacles.update()
        self.bouquets.update()
        self.boosts.update()
        self.enemies.update()
        self.player.projectiles.update()
        self.check_bouquet_collisions()
        self.check_boost_collisions()  # Проверка столкновений с бустами
        self.player.update_shoot_cooldown()  # Обновляем состояние стрельбы
        self.check_enemy_collisions()  # Новая проверка на уничтожение врагов
        self.check_collisions()

        if self.player.death_animation_done:
            return 'lose'

        if pygame.sprite.collide_rect(self.player, self.bride) or pygame.sprite.spritecollideany(self.player, self.enemies):
            self.player.dead = True

        if self.score >= 100:
            return 'win'
        return None

    def draw(self, screen):
        for i, bg in enumerate(self.background_images):
            screen.blit(bg, (self.background_x + i * SCREEN_WIDTH, 0))
            screen.blit(bg, (self.background_x + (i - 1) * SCREEN_WIDTH, 0))
            screen.blit(bg, (self.background_x + (i + 1) * SCREEN_WIDTH, 0))

        for obstacle in self.obstacles:
            screen.blit(obstacle.image, obstacle.rect)
        self.bouquets.draw(screen)
        self.boosts.draw(screen)
        self.player.projectiles.draw(screen)
        self.all_sprites.draw(screen)

        font = pygame.font.SysFont(None, 55)
        score_text = font.render(f'Score: {self.score}', True, (0, 0, 128))
        screen.blit(score_text, (10, SCREEN_HEIGHT - 70))

        bouquet_tracker_image = pygame.image.load('images/level1/bonus-tracker.png').convert_alpha()
        boost_tracker_image = pygame.image.load('images/level1/boost-tracker.png').convert_alpha()
        bouquet_tracker_image = pygame.transform.scale(bouquet_tracker_image, (120, 80))
        boost_tracker_image = pygame.transform.scale(boost_tracker_image, (120, 80))

        screen.blit(bouquet_tracker_image, (SCREEN_WIDTH - 400, SCREEN_HEIGHT - 100))
        bouquet_count_text = font.render(f'{self.player.bouquet_count}', True, (0, 0, 128))
        screen.blit(bouquet_count_text, (SCREEN_WIDTH - 325, SCREEN_HEIGHT - 75))

        screen.blit(boost_tracker_image, (SCREEN_WIDTH - 160, SCREEN_HEIGHT - 100))
        boost_count_text = font.render(f'{self.player.boost_count}', True, (0, 0, 128))
        screen.blit(boost_count_text, (SCREEN_WIDTH - 92, SCREEN_HEIGHT - 75))

    def scroll_background(self, keys):
        player_moving_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        player_moving_left = keys[pygame.K_LEFT] or keys[pygame.K_a]

        scroll_speed = self.player.speed  # Используем текущую скорость игрока для прокрутки

        if player_moving_right:
            self.background_x -= scroll_speed
            for obstacle in self.obstacles:
                obstacle.rect.x -= scroll_speed
            for bouquet in self.bouquets:
                bouquet.rect.x -= scroll_speed
            for boost in self.boosts:
                boost.rect.x -= scroll_speed
            for enemy in self.enemies:
                enemy.rect.x -= scroll_speed

        if player_moving_left and self.background_x < 0:  # Ограничиваем движение влево
            self.background_x += scroll_speed
            for obstacle in self.obstacles:
                obstacle.rect.x += scroll_speed
            for bouquet in self.bouquets:
                bouquet.rect.x += scroll_speed
            for boost in self.boosts:
                boost.rect.x += scroll_speed
            for enemy in self.enemies:
                enemy.rect.x += scroll_speed

        if self.background_x <= -SCREEN_WIDTH:
            self.background_x = 0
            self.background_images.append(self.background_images.pop(0))
        elif self.background_x >= SCREEN_WIDTH:
            self.background_x = 0
            self.background_images.insert(0, self.background_images.pop())

        # Жених остается в центре экрана независимо от направления движения
        self.player.rect.centerx = SCREEN_WIDTH // 2


    def check_enemy_collisions(self):
        for projectile in self.player.projectiles:
            enemy_hit = pygame.sprite.spritecollideany(projectile, self.enemies)
            if enemy_hit:
                enemy_hit.kill()
                projectile.kill()
                self.score += 10  # Пример добавления очков за уничтожение врага

        if pygame.sprite.spritecollideany(self.player, self.enemies):
            self.player.dead = True  # Жених умирает при столкновении с тещей


    def check_boost_collisions(self):
        # Проверка столкновений с бустами
        collided_boosts = pygame.sprite.spritecollide(self.player, self.boosts, True)
        for boost in collided_boosts:
            self.player.boost()

    def check_collisions(self):
        # Проверка столкновений с врагами
        if pygame.sprite.spritecollideany(self.player, self.enemies):
            self.player.rect.x = self.player_start_x  # Возвращаем в начало уровня

    def check_enemy_collisions(self):
        for projectile in self.player.projectiles:
            enemy_hit = pygame.sprite.spritecollideany(projectile, self.enemies)
            if enemy_hit:
                enemy_hit.kill()
                projectile.kill()
                self.score += 10  # Пример добавления очков за уничтожение врага


class Level2(Level):
    def __init__(self, player_images, enemy_images, bride_images):
        background_images = [
            "images/level2/background-1.png",
            "images/level2/background-2.png",
            "images/level2/background-3.png"
        ]
        bouquet_image = pygame.image.load("images/bonus/flowers/flowers0.png").convert_alpha()  # Изображение букета
        super().__init__(player_images, enemy_images, bouquet_image, background_images)

        platform_positions = [
            (SCREEN_WIDTH + 55, SCREEN_HEIGHT - 300),
            (SCREEN_WIDTH + 400, SCREEN_HEIGHT - 350),
            (SCREEN_WIDTH + 725, SCREEN_HEIGHT - 400),
            (SCREEN_WIDTH + 1050, SCREEN_HEIGHT - 300),
            (SCREEN_WIDTH + 1375, SCREEN_HEIGHT - 350),
            (SCREEN_WIDTH + 1700, SCREEN_HEIGHT - 300),
            (SCREEN_WIDTH + 2025, SCREEN_HEIGHT - 350),
            (SCREEN_WIDTH + 2350, SCREEN_HEIGHT - 400),
            (SCREEN_WIDTH + 2675, SCREEN_HEIGHT - 300),
            (SCREEN_WIDTH + 3000, SCREEN_HEIGHT - 350),
            (SCREEN_WIDTH + 3325, SCREEN_HEIGHT - 400),
            (SCREEN_WIDTH + 3650, SCREEN_HEIGHT - 300),
            (SCREEN_WIDTH + 3975, SCREEN_HEIGHT - 350),
            (SCREEN_WIDTH + 4300, SCREEN_HEIGHT - 400),
            (SCREEN_WIDTH + 4625, SCREEN_HEIGHT - 300),
            (SCREEN_WIDTH + 4950, SCREEN_HEIGHT - 350),
            (SCREEN_WIDTH + 5275, SCREEN_HEIGHT - 400),
            (SCREEN_WIDTH + 5600, SCREEN_HEIGHT - 300),
            (SCREEN_WIDTH + 5925, SCREEN_HEIGHT - 350),
            (SCREEN_WIDTH + 6250, SCREEN_HEIGHT - 300),
            (SCREEN_WIDTH + 6575, SCREEN_HEIGHT - 350),
            (SCREEN_WIDTH + 6900, SCREEN_HEIGHT - 400),
            (SCREEN_WIDTH + 7225, SCREEN_HEIGHT - 300),
            (SCREEN_WIDTH + 7550, SCREEN_HEIGHT - 350),
            (SCREEN_WIDTH + 7875, SCREEN_HEIGHT - 400)
        ]
        platform_images = [
            "images/level2/platform-1.png",
            "images/level2/platform-2.png",
            "images/level2/platform-3.png",
            "images/level2/platform-4.png",
            "images/level2/platform-5.png",
            "images/level2/platform-6.png",
            "images/level2/platform-7.png",
            "images/level2/platform-8.png",
            "images/level2/platform-9.png",
            "images/level2/platform-10.png",
            "images/level2/platform-11.png",
            "images/level2/platform-12.png",
            "images/level2/platform-13.png",
            "images/level2/platform-14.png"
        ] * 2  # Увеличиваем количество платформ в два раза

        bouquet_positions = [
            (SCREEN_WIDTH + 55, SCREEN_HEIGHT - 390),
            (SCREEN_WIDTH + 725, SCREEN_HEIGHT - 490),
            (SCREEN_WIDTH + 1700, SCREEN_HEIGHT - 390),
            (SCREEN_WIDTH + 2025, SCREEN_HEIGHT - 440),
            (SCREEN_WIDTH + 3000, SCREEN_HEIGHT - 440),
            (SCREEN_WIDTH + 3650, SCREEN_HEIGHT - 390),
            (SCREEN_WIDTH + 4300, SCREEN_HEIGHT - 490),
            (SCREEN_WIDTH + 4950, SCREEN_HEIGHT - 490),
            (SCREEN_WIDTH + 5600, SCREEN_HEIGHT - 440),
            (SCREEN_WIDTH + 6250, SCREEN_HEIGHT - 390),
            (SCREEN_WIDTH + 6900, SCREEN_HEIGHT - 440),
            (SCREEN_WIDTH + 7550, SCREEN_HEIGHT - 490)
        ]
        bouquet_images = [
            'images/bonus/flowers/flowers0.png',
            'images/bonus/flowers/flowers1.png',
            'images/bonus/flowers/flowers2.png'
        ]
        enemy_positions = [
            (SCREEN_WIDTH + 730, SCREEN_HEIGHT - 390),
            (SCREEN_WIDTH + 3650, SCREEN_HEIGHT - 290),
            (SCREEN_WIDTH + 7550, SCREEN_HEIGHT - 390)
        ]
        boost_positions = [
            (SCREEN_WIDTH + 500, SCREEN_HEIGHT - 400),
            (SCREEN_WIDTH + 2500, SCREEN_HEIGHT - 450),
            (SCREEN_WIDTH + 4500, SCREEN_HEIGHT - 400),
            (SCREEN_WIDTH + 6500, SCREEN_HEIGHT - 450)
        ]
        candle_positions = [
            (SCREEN_WIDTH + 1000, SCREEN_HEIGHT - 190),
            (SCREEN_WIDTH + 3200, SCREEN_HEIGHT - 190),
            (SCREEN_WIDTH + 6000, SCREEN_HEIGHT - 190)
        ]

        # Добавление двигающихся платформ
        moving_platforms = [
            (SCREEN_WIDTH + 100, SCREEN_HEIGHT - 250, "images/level2/platform-1.png", 'horizontal', 200, 2),
            (SCREEN_WIDTH + 1200, SCREEN_HEIGHT - 350, "images/level2/platform-2.png", 'vertical', 150, 2),
            (SCREEN_WIDTH + 2300, SCREEN_HEIGHT - 400, "images/level2/platform-3.png", 'horizontal', 300, 2)
        ]

        for x, y, img, direction, range, speed in moving_platforms:
            platform = MovingPlatform(x, y, img, direction, range, speed)
            self.obstacles.add(platform)
            self.all_sprites.add(platform)

        # Добавление статичных платформ
        for pos, img in zip(platform_positions, platform_images):
            obstacle = Obstacle(pos[0], pos[1], img)
            self.obstacles.add(obstacle)
            self.all_sprites.add(obstacle)

        # Добавление букетовы
        for k, (x, y) in enumerate(bouquet_positions):
            image = bouquet_images[k % len(bouquet_images)]
            bouquet = Bouquet(x, y, image)
            self.bouquets.add(bouquet)
            self.all_sprites.add(bouquet)

        # Добавление бустов
        for (x, y) in boost_positions:
            boost = Boost(x, y, "images/boost/rings/rings0.png")
            self.boosts.add(boost)
            self.all_sprites.add(boost)

        # Добавление врагов
        for pos in enemy_positions:
            enemy = StationaryEnemy(pos[0], pos[1], enemy_images['evil_priest'])
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

        # Добавление подсвечников
        for (x, y) in candle_positions:
            candle = Obstacle(x, y, "images/obstacles/candles/candles.png")
            self.obstacles.add(candle)
            self.all_sprites.add(candle)

        # Добавление невесты
        self.bride = Bride(bride_images, self.player)
        self.all_sprites.add(self.bride)

    def update(self, keys):
        self.player.update(keys, self.obstacles)
        self.bride.update()  # Обновляем невесту
        self.scroll_background(keys)
        self.obstacles.update()
        self.bouquets.update()
        self.boosts.update()
        self.enemies.update()
        self.player.projectiles.update()
        self.check_bouquet_collisions()
        self.check_boost_collisions()  # Проверка столкновений с бустами
        self.player.update_shoot_cooldown()  # Обновляем состояние стрельбы
        self.check_enemy_collisions()  # Новая проверка на уничтожение врагов

        if self.player.death_animation_done:
            return 'lose'

        if pygame.sprite.collide_rect(self.player, self.bride) or pygame.sprite.spritecollideany(self.player, self.enemies):
            self.player.dead = True

        if self.score >= 100:
            return 'win'
        return None

    def draw(self, screen):
        for i, bg in enumerate(self.background_images):
            screen.blit(bg, (self.background_x + i * SCREEN_WIDTH, 0))
            screen.blit(bg, (self.background_x + (i - 1) * SCREEN_WIDTH, 0))
            screen.blit(bg, (self.background_x + (i + 1) * SCREEN_WIDTH, 0))

        for obstacle in self.obstacles:
            screen.blit(obstacle.image, obstacle.rect)
        self.bouquets.draw(screen)
        self.boosts.draw(screen)
        self.player.projectiles.draw(screen)
        self.all_sprites.draw(screen)

        font = pygame.font.SysFont(None, 55)
        score_text = font.render(f'Score: {self.score}', True, (0, 0, 128))
        screen.blit(score_text, (10, SCREEN_HEIGHT - 70))

        bouquet_tracker_image = pygame.image.load('images/level1/bonus-tracker.png').convert_alpha()
        boost_tracker_image = pygame.image.load('images/level1/boost-tracker.png').convert_alpha()
        bouquet_tracker_image = pygame.transform.scale(bouquet_tracker_image, (120, 80))
        boost_tracker_image = pygame.transform.scale(boost_tracker_image, (120, 80))

        screen.blit(bouquet_tracker_image, (SCREEN_WIDTH - 400, SCREEN_HEIGHT - 100))
        bouquet_count_text = font.render(f'{self.player.bouquet_count}', True, (0, 0, 128))
        screen.blit(bouquet_count_text, (SCREEN_WIDTH - 325, SCREEN_HEIGHT - 75))

        screen.blit(boost_tracker_image, (SCREEN_WIDTH - 160, SCREEN_HEIGHT - 100))
        boost_count_text = font.render(f'{self.player.boost_count}', True, (0, 0, 128))
        screen.blit(boost_count_text, (SCREEN_WIDTH - 92, SCREEN_HEIGHT - 75))