import pygame
from constants import *

class Menu:
    def __init__(self):
        self.font_title = pygame.font.SysFont("Arial", 64, bold=True)
        self.font_button = pygame.font.SysFont("Arial", 32)
        
        # Button rectangles
        self.btn_3_players = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 60)
        self.btn_4_players = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 60)

    def draw(self, surface):
        surface.fill(BACKGROUND)
        
        # Title
        title = self.font_title.render("Catan Placement Simulator", True, BLACK)
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//4))
        surface.blit(title, title_rect)

        # Buttons
        self._draw_button(surface, self.btn_3_players, "3 Players")
        self._draw_button(surface, self.btn_4_players, "4 Players")

    def _draw_button(self, surface, rect, text):
        pygame.draw.rect(surface, WHITE, rect)
        pygame.draw.rect(surface, BLACK, rect, 3)
        text_surf = self.font_button.render(text, True, BLACK)
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        """Returns the number of players selected, or None if no selection."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_3_players.collidepoint(event.pos):
                return 3
            if self.btn_4_players.collidepoint(event.pos):
                return 4
        return None