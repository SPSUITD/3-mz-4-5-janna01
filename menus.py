import pygame
from screen_vars import SCREEN_WIDTH, SCREEN_HEIGHT

class Menu:
    def __init__(self, screen, background_image):
        self.screen = screen
        background = pygame.image.load(background_image).convert()
        self.background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

    def display_menu(self):
        self.screen.blit(self.background, (0, 0))

class MainMenu(Menu):
    def __init__(self, screen):
        super().__init__(screen, "images/main-menu/background.png")
        start_button_image = pygame.image.load("images/main-menu/button-start.png").convert_alpha()
        exit_button_image = pygame.image.load("images/main-menu/button-exit.png").convert_alpha()

        # Уменьшение размера кнопок
        self.start_button = pygame.transform.scale(start_button_image, (start_button_image.get_width() // 2, start_button_image.get_height() // 2))
        self.exit_button = pygame.transform.scale(exit_button_image, (exit_button_image.get_width() // 2, exit_button_image.get_height() // 2))

        self.start_rect = self.start_button.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.exit_rect = self.exit_button.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

    def display_menu(self): 
        super().display_menu()
        self.screen.blit(self.start_button, self.start_rect.topleft)
        self.screen.blit(self.exit_button, self.exit_rect.topleft)
        pygame.display.flip()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_rect.collidepoint(event.pos):
                return 'start'
            elif self.exit_rect.collidepoint(event.pos):
                return 'exit'
        return None

class WinMenu(Menu):
    def __init__(self, screen):
        super().__init__(screen, "images/win-menu/background.png")
        self.font = pygame.font.Font(None, 74)
        self.next_level_button = pygame.image.load("images/win-menu/next-level-button.png").convert_alpha()
        self.exit_button = pygame.image.load("images/win-menu/exit-button.png").convert_alpha()

        # Уменьшение размера кнопок
        self.next_level_button = pygame.transform.scale(self.next_level_button, (self.next_level_button.get_width() // 2, self.next_level_button.get_height() // 2))
        self.exit_button = pygame.transform.scale(self.exit_button, (self.exit_button.get_width() // 2, self.exit_button.get_height() // 2))

        self.next_level_rect = self.next_level_button.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.exit_rect = self.exit_button.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

    def display_menu(self):
        super().display_menu()
        self.screen.blit(self.next_level_button, self.next_level_rect.topleft)
        self.screen.blit(self.exit_button, self.exit_rect.topleft)
        pygame.display.flip()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.next_level_rect.collidepoint(event.pos):
                return 'next_level'
            elif self.exit_rect.collidepoint(event.pos):
                return 'exit'
        return None


class LoseMenu(Menu):
    def __init__(self, screen):
        super().__init__(screen, "images/lose-menu/background.png")
        self.font = pygame.font.Font(None, 74)
        self.restart_button = pygame.image.load("images/lose-menu/restart-button.png").convert_alpha()
        self.exit_button = pygame.image.load("images/lose-menu/exit-button.png").convert_alpha()

        # Уменьшение размера кнопок
        self.restart_button = pygame.transform.scale(self.restart_button, (self.restart_button.get_width() // 2, self.restart_button.get_height() // 2))
        self.exit_button = pygame.transform.scale(self.exit_button, (self.exit_button.get_width() // 2, self.exit_button.get_height() // 2))

        self.restart_rect = self.restart_button.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.exit_rect = self.exit_button.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

    def display_menu(self):
        super().display_menu()
        self.screen.blit(self.restart_button, self.restart_rect.topleft)
        self.screen.blit(self.exit_button, self.exit_rect.topleft)
        pygame.display.flip()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.restart_rect.collidepoint(event.pos):
                return 'restart'
            elif self.exit_rect.collidepoint(event.pos):
                return 'exit'
        return None
