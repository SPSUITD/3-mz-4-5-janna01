import pygame
from levels import Level1, Level2
from menus import MainMenu, WinMenu, LoseMenu

def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    running = True

    # Инициализация уровней и меню
    level1 = Level1()
    level2 = Level2()
    main_menu = MainMenu(screen)
    win_menu = WinMenu(screen)
    lose_menu = LoseMenu(screen)

    current_level = level1
    show_main_menu = True
    show_win_menu = False
    show_lose_menu = False

    while running:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if show_main_menu:
            main_menu.display_menu()
            if keys[pygame.K_RETURN]:
                show_main_menu = False
        elif show_win_menu:
            win_menu.display_menu()
            if keys[pygame.K_RETURN]:
                show_win_menu = False
                current_level = level1  # Начать заново с первого уровня
        elif show_lose_menu:
            lose_menu.display_menu()
            if keys[pygame.K_RETURN]:
                show_lose_menu = False
                current_level = level1  # Начать заново с первого уровня
        else:
            current_level.update(keys)
            screen.fill((0, 0, 0))
            current_level.draw(screen)
            pygame.display.flip()

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
