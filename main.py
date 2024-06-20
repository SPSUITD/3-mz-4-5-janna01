import pygame
import sys
from levels import Level1, Level2
from menus import MainMenu, WinMenu, LoseMenu
import os
from screen_vars import SCREEN_WIDTH, SCREEN_HEIGHT

# Инициализация Pygame
pygame.init()

# Настройки окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Wedding Escape")

# Функция для загрузки изображений
def load_images(path_list):
    images = []
    for path in path_list:
        if os.path.exists(path):
            images.append(pygame.image.load(path).convert_alpha())
        else:
            print(f"File not found: {path}")
            raise FileNotFoundError(f"No file '{path}' found in working directory")
    return images

# Загрузка изображений для анимаций
player_images = {
    'idle': load_images([
        'images/groom-right/groom0.png'
    ]),
    'run': load_images([
        'images/groom-right/groom1.png',
        'images/groom-right/groom2.png',
        'images/groom-right/groom3.png',
        'images/groom-right/groom4.png',
        'images/groom-right/groom5.png'
    ]),
    'jump': load_images([
        'images/groom-jump/groom-jump-0.png',
        'images/groom-jump/groom-jump-1.png',
        'images/groom-jump/groom-jump-2.png',
        'images/groom-jump/groom-jump-3.png',
        'images/groom-jump/groom-jump-4.png'
    ]),
    'death': load_images([
        'images/groom-death/groom_death_0.png',
        'images/groom-death/groom_death_1.png',
        'images/groom-death/groom_death_2.png',
        'images/groom-death/groom_death_3.png',
        'images/groom-death/groom_death_4.png',
        'images/groom-death/groom_death_5.png'
    ]),
    'attack': load_images([
        'images/groom-strelba/groom_strelba0.png',
        'images/groom-strelba/groom_strelba1.png',
        'images/groom-strelba/groom_strelba2.png',
        'images/groom-strelba/groom_strelba3.png',
        'images/groom-strelba/groom_strelba4.png'
    ])
}

# Загрузка изображений для анимаций невесты
bride_images = {
    'idle': [pygame.image.load("images/bride-right/bride0.png").convert_alpha()],
    'run_right': [
        pygame.image.load("images/bride-right/bride0.png").convert_alpha(),
        pygame.image.load("images/bride-right/bride1.png").convert_alpha(),
        pygame.image.load("images/bride-right/bride2.png").convert_alpha(),
        pygame.image.load("images/bride-right/bride3.png").convert_alpha(),
        pygame.image.load("images/bride-right/bride4.png").convert_alpha()
    ],
    'run_left': [
        pygame.image.load("images/bride-left/bride_left0.png").convert_alpha(),
        pygame.image.load("images/bride-left/bride_left1.png").convert_alpha(),
        pygame.image.load("images/bride-left/bride_left2.png").convert_alpha(),
        pygame.image.load("images/bride-left/bride_left3.png").convert_alpha(),
        pygame.image.load("images/bride-left/bride_left4.png").convert_alpha()
    ],
    'jump': [
        pygame.image.load("images/bride-jump/bride-jump-0.png").convert_alpha(),
        pygame.image.load("images/bride-jump/bride-jump-1.png").convert_alpha(),
        pygame.image.load("images/bride-jump/bride-jump-2.png").convert_alpha(),
        pygame.image.load("images/bride-jump/bride-jump-3.png").convert_alpha(),
        pygame.image.load("images/bride-jump/bride-jump-4.png").convert_alpha()
    ]
}


enemy_images = {
    'teshya': {
        'idle': load_images(['images/enemies/teshya/teshya0.png', 'images/enemies/teshya/teshya1.png']),
        'attack': load_images(['images/enemies/teshya/teshya1.png'])
    },
    'evil_priest': {
        'idle': load_images(['images/enemies/evil-priest/evil-priest-0.png', 'images/enemies/evil-priest/evil-priest-1.png']),
        'attack': load_images(['images/enemies/evil-priest/evil-priest-1.png'])
    }
}


def main():
    clock = pygame.time.Clock()
    running = True

    # Инициализация уровней и меню
    level1 = Level1(player_images, enemy_images, bride_images)
    level2 = Level2(player_images, enemy_images, bride_images)
    main_menu = MainMenu(screen)
    win_menu = WinMenu(screen)
    lose_menu = LoseMenu(screen)

    levels = [level1, level2]
    current_level_index = 0
    current_level = levels[current_level_index]
    show_main_menu = True
    show_win_menu = False
    show_lose_menu = False

    while running:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if show_main_menu:
                result = main_menu.handle_event(event)
                if result == 'start':
                    show_main_menu = False
                    current_level_index = 0  # Начать с первого уровня
                    current_level = levels[current_level_index]
                elif result == 'exit':
                    running = False

            elif show_win_menu:
                result = win_menu.handle_event(event)
                if result == 'next_level':
                    show_win_menu = False
                    current_level_index = (current_level_index + 1) % len(levels)
                    current_level = levels[current_level_index]  # Переход на следующий уровень
                elif result == 'exit':
                    show_win_menu = False
                    show_main_menu = True

            elif show_lose_menu:
                result = lose_menu.handle_event(event)
                if result == 'restart':
                    show_lose_menu = False
                    levels[current_level_index] = Level1(player_images, enemy_images, bride_images) if current_level_index == 0 else Level2(player_images, enemy_images, bride_images)
                    current_level = levels[current_level_index]  # Перезапуск текущего уровня
                elif result == 'exit':
                    running = False  # Завершить главный цикл и выйти из игры

        if show_main_menu:
            main_menu.display_menu()
        elif show_win_menu:
            win_menu.display_menu()
        elif show_lose_menu:
            lose_menu.display_menu()
        else:
            level_status = current_level.update(keys)
            screen.fill((0, 0, 0))
            current_level.draw(screen)
            pygame.display.flip()

            # Проверка условий победы и поражения
            if level_status == 'win':
                show_win_menu = True
            if level_status == 'lose':  # Если проиграна анимация смерти
                show_lose_menu = True
            if current_level.player.rect.y > SCREEN_HEIGHT:  # Пример условия поражения
                show_lose_menu = True

        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
