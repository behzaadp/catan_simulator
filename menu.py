import pygame
from constants import *

class Button:
    def __init__(self, rect, text, font):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.is_hovered = False

    def draw(self, surface):
        # Determine colors based on hover state
        bg_color = WHITE if self.is_hovered else GLASS_BG_DARK
        text_color = BLACK if self.is_hovered else WHITE
        
        # Draw Drop Shadow
        shadow_rect = self.rect.copy()
        shadow_rect.y += SHADOW_OFFSET
        # We use a Surface to support alpha channel shadows
        shadow_surf = pygame.Surface(shadow_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, SHADOW_COLOR, shadow_surf.get_rect(), border_radius=30)
        surface.blit(shadow_surf, shadow_rect.topleft)
        
        # Draw Pill Button
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=30)
        if not self.is_hovered:
            pygame.draw.rect(surface, SUBTLE_GRAY, self.rect, 2, border_radius=30)
        
        # Draw Text
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)


class Menu:
    def __init__(self):
        # Load premium typography
        self.font_title = get_font(52, "ui")
        self.font_subtitle = get_font(20, "ui")
        self.font_button = get_font(24, "ui")
        
        # Center buttons
        btn_width, btn_height = 240, 60
        self.btn_3_players = Button((WIDTH//2 - btn_width//2, HEIGHT//2, btn_width, btn_height), "3 Players", self.font_button)
        self.btn_4_players = Button((WIDTH//2 - btn_width//2, HEIGHT//2 + 80, btn_width, btn_height), "4 Players", self.font_button)

        # Pre-generate the Ocean Gradient Background
        self.bg_surface = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            r = OCEAN_BG_DARK[0] + (OCEAN_BG_LIGHT[0] - OCEAN_BG_DARK[0]) * y // HEIGHT
            g = OCEAN_BG_DARK[1] + (OCEAN_BG_LIGHT[1] - OCEAN_BG_DARK[1]) * y // HEIGHT
            b = OCEAN_BG_DARK[2] + (OCEAN_BG_LIGHT[2] - OCEAN_BG_DARK[2]) * y // HEIGHT
            pygame.draw.line(self.bg_surface, (r, g, b), (0, y), (WIDTH, y))

    def draw(self, surface, mouse_pos):
        # Draw Gradient Background
        surface.blit(self.bg_surface, (0, 0))
        
        # Title Typography
        title_text = "CATAN PLACEMENT"
        subtitle_text = "E X E C U T I V E   S I M U L A T O R"
        
        # Title Shadow
        t_shadow = self.font_title.render(title_text, True, SHADOW_COLOR)
        s_shadow = self.font_subtitle.render(subtitle_text, True, SHADOW_COLOR)
        surface.blit(t_shadow, t_shadow.get_rect(center=(WIDTH//2, HEIGHT//3 - 30 + SHADOW_OFFSET)))
        surface.blit(s_shadow, s_shadow.get_rect(center=(WIDTH//2, HEIGHT//3 + 20 + SHADOW_OFFSET)))

        # Title Text
        t_surf = self.font_title.render(title_text, True, WHITE)
        s_surf = self.font_subtitle.render(subtitle_text, True, SUBTLE_GRAY)
        surface.blit(t_surf, t_surf.get_rect(center=(WIDTH//2, HEIGHT//3 - 30)))
        surface.blit(s_surf, s_surf.get_rect(center=(WIDTH//2, HEIGHT//3 + 20)))

        # Update Hover States and Draw Buttons
        self.btn_3_players.check_hover(mouse_pos)
        self.btn_4_players.check_hover(mouse_pos)
        self.btn_3_players.draw(surface)
        self.btn_4_players.draw(surface)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_3_players.rect.collidepoint(event.pos):
                return 3
            if self.btn_4_players.rect.collidepoint(event.pos):
                return 4
        return None