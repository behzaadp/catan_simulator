import pygame
import sys
import random
from constants import *
from menu import Menu, Button  # IMPORTANT: We are now importing the premium Button class
from board import Board
from bot import bot_get_best_settlement, bot_get_best_road
from evaluator import evaluate_placements 

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Catan Placement Simulator")
    clock = pygame.time.Clock()

    # Load premium fonts using the new engine
    font_large = get_font(24, "ui")
    font_small = get_font(16, "ui")
    font_ui = get_font(20, "ui")
    font_avatar = get_font(18, "ui")
    font_huge = get_font(64, "ui")      # For the Grade Badge Letter
    font_badge = get_font(14, "ui")     # For the Grade Subtext

    state = "MENU"
    menu = Menu()
    board = None
    
    players = []
    draft_sequence = []
    current_turn_index = 0
    phase = "SETTLEMENT"
    last_placed_node = None
    panel_minimized = False

    # Pre-generate in-game Ocean Gradient Background
    bg_surface = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        r = OCEAN_BG_DARK[0] + (OCEAN_BG_LIGHT[0] - OCEAN_BG_DARK[0]) * y // HEIGHT
        g = OCEAN_BG_DARK[1] + (OCEAN_BG_LIGHT[1] - OCEAN_BG_DARK[1]) * y // HEIGHT
        b = OCEAN_BG_DARK[2] + (OCEAN_BG_LIGHT[2] - OCEAN_BG_DARK[2]) * y // HEIGHT
        pygame.draw.line(bg_surface, (r, g, b), (0, y), (WIDTH, y))

    # Initialize premium Buttons (positions will be dynamically updated based on panel state)
    btn_play_again = Button((0, 0, 1, 1), "Play Again", font_ui)
    btn_menu = Button((0, 0, 1, 1), "Main Menu", font_ui)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        # Dynamically position the UI boundaries based on toggle state
        if panel_minimized:
            panel_rect = pygame.Rect(20, HEIGHT - 90, WIDTH - 40, 70)
            toggle_rect = pygame.Rect(panel_rect.right - 130, panel_rect.top + 15, 110, 40)
            btn_play_again.rect = pygame.Rect(panel_rect.right - 330, panel_rect.top + 15, 180, 40)
            btn_menu.rect = pygame.Rect(panel_rect.right - 490, panel_rect.top + 15, 140, 40)
        else:
            panel_rect = pygame.Rect(20, HEIGHT - 360, WIDTH - 40, 340)
            toggle_rect = pygame.Rect(panel_rect.right - 130, panel_rect.top + 20, 110, 40)
            btn_play_again.rect = pygame.Rect(panel_rect.right - 200, panel_rect.bottom - 60, 180, 40)
            btn_menu.rect = pygame.Rect(panel_rect.right - 360, panel_rect.bottom - 60, 140, 40)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if state == "MENU":
                selection = menu.handle_event(event)
                if selection:
                    players = [{"name": "You", "color": PLAYER_COLORS[0], "is_bot": False}]
                    for i in range(1, selection):
                        players.append({"name": f"Bot {i}", "color": PLAYER_COLORS[i], "is_bot": True})
                    
                    random.shuffle(players)
                    draft_sequence = list(range(selection)) + list(range(selection - 1, -1, -1))
                    current_turn_index = 0
                    phase = "SETTLEMENT"
                    board = Board()
                    state = "GAME"
                    panel_minimized = False 
                    
            elif state == "GAME":
                if phase != "FINISHED":
                    current_player = players[draft_sequence[current_turn_index]]
                    
                    if not current_player["is_bot"] and event.type == pygame.MOUSEBUTTONDOWN:
                        if phase == "SETTLEMENT":
                            clicked_node = board.get_clicked_node(event.pos)
                            if clicked_node and board.is_valid_settlement(clicked_node):
                                clicked_node.building = current_player["color"]
                                last_placed_node = clicked_node
                                phase = "ROAD"
                                
                        elif phase == "ROAD":
                            clicked_edge = board.get_clicked_edge(event.pos)
                            if clicked_edge and board.is_valid_initial_road(clicked_edge, last_placed_node):
                                clicked_edge.road = current_player["color"]
                                current_turn_index += 1
                                if current_turn_index >= len(draft_sequence):
                                    phase = "FINISHED"
                                else:
                                    phase = "SETTLEMENT"
                else:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if toggle_rect.collidepoint(event.pos):
                            panel_minimized = not panel_minimized
                        elif btn_play_again.rect.collidepoint(event.pos):
                            random.shuffle(players)
                            draft_sequence = list(range(len(players))) + list(range(len(players) - 1, -1, -1))
                            current_turn_index = 0
                            phase = "SETTLEMENT"
                            last_placed_node = None
                            panel_minimized = False
                            board = Board()
                        elif btn_menu.rect.collidepoint(event.pos):
                            state = "MENU"

        if state == "GAME" and phase != "FINISHED":
            current_player = players[draft_sequence[current_turn_index]]
            if current_player["is_bot"]:
                pygame.time.delay(400)
                if phase == "SETTLEMENT":
                    node = bot_get_best_settlement(board)
                    node.building = current_player["color"]
                    last_placed_node = node
                    phase = "ROAD"
                elif phase == "ROAD":
                    edge = bot_get_best_road(board, last_placed_node)
                    edge.road = current_player["color"]
                    current_turn_index += 1
                    if current_turn_index >= len(draft_sequence):
                        phase = "FINISHED"
                    else:
                        phase = "SETTLEMENT"

        # --- DRAWING PHASE ---
        if state == "MENU":
            menu.draw(screen, mouse_pos)
        elif state == "GAME":
            screen.blit(bg_surface, (0, 0))
            board.draw(screen, font_large, font_small)
            
            if phase != "FINISHED":
                # TOP BAR TURN TRACKER
                tracker_w = len(draft_sequence) * 50 + 40
                tracker_h = 60
                tracker_x = (WIDTH - tracker_w) // 2
                tracker_y = 20
                
                pill_surf = pygame.Surface((tracker_w, tracker_h), pygame.SRCALPHA)
                pygame.draw.rect(pill_surf, (*GLASS_BG_DARK, 220), pill_surf.get_rect(), border_radius=30)
                pygame.draw.rect(pill_surf, (*SUBTLE_GRAY, 80), pill_surf.get_rect(), 2, border_radius=30)
                screen.blit(pill_surf, (tracker_x, tracker_y))
                
                for i, p_idx in enumerate(draft_sequence):
                    p_color = players[p_idx]["color"]
                    cx = tracker_x + 45 + (i * 50)
                    cy = tracker_y + 30
                    
                    if i == current_turn_index:
                        pygame.draw.circle(screen, WHITE, (cx, cy), 20)
                    
                    pygame.draw.circle(screen, p_color, (cx, cy), 16)
                    
                    initial = players[p_idx]["name"][0]
                    text_col = BLACK if p_color in [WHITE, PLAYER_COLORS[3]] else WHITE
                    init_surf = font_avatar.render(initial, True, text_col)
                    screen.blit(init_surf, init_surf.get_rect(center=(cx, cy)))

                # ACTION BANNER (Floating Center Bottom)
                current_player = players[draft_sequence[current_turn_index]]
                prompt = "Place a Settlement" if phase == "SETTLEMENT" else "Place a Road"
                action_text = f"{current_player['name']}'s Turn: {prompt}"
                
                banner_surf = font_ui.render(action_text, True, WHITE)
                banner_rect = banner_surf.get_rect(center=(WIDTH//2, HEIGHT - 60))
                
                b_bg = pygame.Rect(0, 0, banner_rect.width + 70, 50)
                b_bg.center = banner_rect.center
                b_surf = pygame.Surface(b_bg.size, pygame.SRCALPHA)
                pygame.draw.rect(b_surf, (*GLASS_BG_DARK, 220), b_surf.get_rect(), border_radius=25)
                screen.blit(b_surf, b_bg.topleft)
                
                pygame.draw.circle(screen, current_player["color"], (b_bg.left + 25, b_bg.centery), 10)
                banner_rect.x += 15
                screen.blit(banner_surf, banner_rect)
            
            else:
                # ----------------------------------------------------
                # PHASE 4: PREMIUM EVALUATION DASHBOARD
                # ----------------------------------------------------
                grade_text, pips, feedback = evaluate_placements(board, PLAYER_COLORS[0])
                
                # Split "A (Great)" into "A" and "GREAT"
                grade_letter = grade_text.split(" ")[0]
                grade_subtext = grade_text.split(" ", 1)[1].replace("(","").replace(")","").upper() if " " in grade_text else ""
                
                # Color coded Grade System
                grade_colors = {
                    "S+": (191, 85, 236),  # Radiant Purple
                    "S":  (241, 196, 15),  # Gold
                    "A":  (46, 204, 113),  # Mint Green
                    "B":  (52, 152, 219),  # Azure Blue
                    "C":  (243, 156, 18),  # Amber
                    "D":  (231, 76, 60)    # Crimson Red
                }
                badge_color = grade_colors.get(grade_letter, WHITE)

                # Draw Main Dashboard Glassmorphism Panel
                panel_surf = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(panel_surf, (*GLASS_BG_DARK, 235), panel_surf.get_rect(), border_radius=20)
                pygame.draw.rect(panel_surf, (*SUBTLE_GRAY, 50), panel_surf.get_rect(), 2, border_radius=20)
                screen.blit(panel_surf, panel_rect.topleft)

                # Draw Custom Toggle Button
                is_toggle_hovered = toggle_rect.collidepoint(mouse_pos)
                toggle_bg = (*SUBTLE_GRAY, 100) if is_toggle_hovered else (*SUBTLE_GRAY, 30)
                toggle_surf = pygame.Surface(toggle_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(toggle_surf, toggle_bg, toggle_surf.get_rect(), border_radius=12)
                pygame.draw.rect(toggle_surf, (*SUBTLE_GRAY, 80), toggle_surf.get_rect(), 1, border_radius=12)
                screen.blit(toggle_surf, toggle_rect.topleft)
                
                toggle_label = "Expand ▲" if panel_minimized else "Minimize ▼"
                t_text = font_small.render(toggle_label, True, WHITE)
                screen.blit(t_text, t_text.get_rect(center=toggle_rect.center))

                if panel_minimized:
                    # MINIMIZED STATE (Sleek Horizontal Summary)
                    mini_badge = font_large.render(grade_letter, True, badge_color)
                    screen.blit(mini_badge, (panel_rect.left + 25, panel_rect.top + 20))
                    
                    title = font_ui.render(f"Evaluation: {grade_subtext}", True, WHITE)
                    screen.blit(title, (panel_rect.left + 80, panel_rect.top + 22))
                    
                else:
                    # EXPANDED STATE (Full Analytics View)
                    
                    # 1. The Grade Badge
                    badge_rect = pygame.Rect(panel_rect.left + 30, panel_rect.top + 30, 130, 130)
                    badge_surf = pygame.Surface(badge_rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(badge_surf, (*badge_color, 25), badge_surf.get_rect(), border_radius=25)
                    pygame.draw.rect(badge_surf, badge_color, badge_surf.get_rect(), 3, border_radius=25)
                    screen.blit(badge_surf, badge_rect.topleft)
                    
                    g_letter_surf = font_huge.render(grade_letter, True, badge_color)
                    screen.blit(g_letter_surf, g_letter_surf.get_rect(center=(badge_rect.centerx, badge_rect.centery - 10)))
                    
                    g_text_surf = font_badge.render(grade_subtext, True, badge_color)
                    screen.blit(g_text_surf, g_text_surf.get_rect(center=(badge_rect.centerx, badge_rect.bottom - 20)))

                    # 2. Production Metric
                    pip_title = font_small.render("RAW PRODUCTION", True, SUBTLE_GRAY)
                    screen.blit(pip_title, (panel_rect.left + 190, panel_rect.top + 35))
                    
                    pip_val = font_large.render(f"{pips} Pips", True, WHITE)
                    screen.blit(pip_val, (panel_rect.left + 190, panel_rect.top + 55))

                    # 3. Analytics List with Geometric Pygame Icons
                    fb_start_x = panel_rect.left + 190
                    fb_start_y = panel_rect.top + 105
                    
                    for i, fb in enumerate(feedback):
                        # Detect negative feedback words to color-code the icons
                        is_warning = any(w in fb for w in ["Poor", "CRITICAL", "Warning", "Weak", "Wasted", "blocked", "dead end"])
                        icon_col = (231, 76, 60) if is_warning else (46, 204, 113)
                        
                        icon_cx = fb_start_x + 12
                        icon_cy = fb_start_y + (i * 28) + 10
                        
                        # Draw Icon Ring
                        icon_bg = (
                            GLASS_BG_DARK[0] + icon_col[0]//5, 
                            GLASS_BG_DARK[1] + icon_col[1]//5, 
                            GLASS_BG_DARK[2] + icon_col[2]//5
                        )
                        pygame.draw.circle(screen, icon_bg, (icon_cx, icon_cy), 10)
                        pygame.draw.circle(screen, icon_col, (icon_cx, icon_cy), 10, 2)
                        
                        # Draw Custom Geometry inside the Ring
                        if not is_warning:
                            # Checkmark
                            pygame.draw.line(screen, icon_col, (icon_cx - 4, icon_cy), (icon_cx - 1, icon_cy + 4), 2)
                            pygame.draw.line(screen, icon_col, (icon_cx - 1, icon_cy + 4), (icon_cx + 5, icon_cy - 4), 2)
                        else:
                            # Exclamation Point
                            pygame.draw.line(screen, icon_col, (icon_cx, icon_cy - 4), (icon_cx, icon_cy + 1), 2)
                            pygame.draw.line(screen, icon_col, (icon_cx, icon_cy + 4), (icon_cx, icon_cy + 5), 2)
                        
                        fb_text = font_small.render(fb, True, (240, 240, 240))
                        screen.blit(fb_text, (fb_start_x + 35, fb_start_y + (i * 28)))

                # Update hover states and render buttons
                btn_play_again.check_hover(mouse_pos)
                btn_menu.check_hover(mouse_pos)
                btn_play_again.draw(screen)
                btn_menu.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()