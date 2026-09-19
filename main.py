import pygame
import sys
import random
from constants import *
from menu import Menu
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

    btn_play_again = pygame.Rect(WIDTH - 220, 20, 200, 50)
    btn_menu = pygame.Rect(WIDTH - 220, 80, 200, 50)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

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
                        if panel_minimized:
                            btn_toggle = pygame.Rect(WIDTH - 130, HEIGHT - 55, 110, 30)
                        else:
                            btn_toggle = pygame.Rect(WIDTH - 130, HEIGHT - 325, 110, 30)
                        
                        if btn_toggle.collidepoint(event.pos):
                            panel_minimized = not panel_minimized
                        elif btn_play_again.collidepoint(event.pos):
                            random.shuffle(players)
                            draft_sequence = list(range(len(players))) + list(range(len(players) - 1, -1, -1))
                            current_turn_index = 0
                            phase = "SETTLEMENT"
                            last_placed_node = None
                            panel_minimized = False
                            board = Board()
                        elif btn_menu.collidepoint(event.pos):
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
            # Draw premium ocean background
            screen.blit(bg_surface, (0, 0))
            
            # Draw Board (Will be heavily upgraded in Phase 3)
            board.draw(screen, font_large, font_small)
            
            if phase != "FINISHED":
                # ----------------------------------------------------
                # NEW HUD: TOP BAR TURN TRACKER (Glassmorphism Pill)
                # ----------------------------------------------------
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
                    
                    # Highlight Active Player with glowing white ring
                    if i == current_turn_index:
                        pygame.draw.circle(screen, WHITE, (cx, cy), 20)
                    
                    pygame.draw.circle(screen, p_color, (cx, cy), 16)
                    
                    # Draw Initial Letter (Y for You, B for Bot)
                    initial = players[p_idx]["name"][0]
                    text_col = BLACK if p_color in [WHITE, PLAYER_COLORS[3]] else WHITE
                    init_surf = font_avatar.render(initial, True, text_col)
                    screen.blit(init_surf, init_surf.get_rect(center=(cx, cy)))

                # ----------------------------------------------------
                # NEW HUD: ACTION BANNER (Floating Center Bottom)
                # ----------------------------------------------------
                current_player = players[draft_sequence[current_turn_index]]
                prompt = "Place a Settlement" if phase == "SETTLEMENT" else "Place a Road"
                action_text = f"{current_player['name']}'s Turn: {prompt}"
                
                banner_surf = font_ui.render(action_text, True, WHITE)
                banner_rect = banner_surf.get_rect(center=(WIDTH//2, HEIGHT - 60))
                
                # Banner Background
                b_bg = pygame.Rect(0, 0, banner_rect.width + 70, 50)
                b_bg.center = banner_rect.center
                b_surf = pygame.Surface(b_bg.size, pygame.SRCALPHA)
                pygame.draw.rect(b_surf, (*GLASS_BG_DARK, 220), b_surf.get_rect(), border_radius=25)
                screen.blit(b_surf, b_bg.topleft)
                
                # Player Color Dot on Banner
                pygame.draw.circle(screen, current_player["color"], (b_bg.left + 25, b_bg.centery), 10)
                banner_rect.x += 15 # Shift text right to account for dot
                screen.blit(banner_surf, banner_rect)
            
            else:
                done_text = font_ui.render("Initial Placements Complete!", True, WHITE)
                screen.blit(done_text, (20, 20))

                # --- TEMP EVALUATION PANEL (Will be upgraded in Phase 4) ---
                grade, pips, feedback = evaluate_placements(board, PLAYER_COLORS[0])
                
                if panel_minimized:
                    panel_rect = pygame.Rect(20, HEIGHT - 70, WIDTH - 40, 60)
                    btn_toggle = pygame.Rect(WIDTH - 130, HEIGHT - 55, 110, 30)
                else:
                    panel_rect = pygame.Rect(20, HEIGHT - 340, WIDTH - 40, 320)
                    btn_toggle = pygame.Rect(WIDTH - 130, HEIGHT - 325, 110, 30)

                pygame.draw.rect(screen, GLASS_BG_DARK, panel_rect, border_radius=10)
                pygame.draw.rect(screen, SUBTLE_GRAY, panel_rect, 2, border_radius=10)
                
                pygame.draw.rect(screen, SUBTLE_GRAY, btn_toggle, border_radius=15)
                toggle_label = "Expand ▲" if panel_minimized else "Minimize ▼"
                toggle_text = font_small.render(toggle_label, True, BLACK)
                screen.blit(toggle_text, toggle_text.get_rect(center=btn_toggle.center))

                if panel_minimized:
                    title_text = font_ui.render(f"Evaluation - Grade: {grade}", True, PLAYER_COLORS[0])
                    screen.blit(title_text, (40, HEIGHT - 55))
                else:
                    title_text = font_ui.render(f"Evaluation - Grade: {grade}", True, PLAYER_COLORS[0])
                    screen.blit(title_text, (40, HEIGHT - 325))
                    
                    pip_text = font_ui.render(f"Total Raw Production (Pips): {pips}", True, WHITE)
                    screen.blit(pip_text, (40, HEIGHT - 285))
                    
                    for i, fb in enumerate(feedback):
                        fb_text = font_small.render(f"• {fb}", True, SUBTLE_GRAY)
                        screen.blit(fb_text, (40, HEIGHT - 250 + (i * 25)))

                # Temporary Draw End Game Buttons (To be redesigned in Phase 4)
                pygame.draw.rect(screen, GLASS_BG_DARK, btn_play_again, border_radius=25)
                pygame.draw.rect(screen, SUBTLE_GRAY, btn_play_again, 2, border_radius=25)
                pa_text = font_ui.render("Play Again", True, WHITE)
                screen.blit(pa_text, pa_text.get_rect(center=btn_play_again.center))

                pygame.draw.rect(screen, GLASS_BG_DARK, btn_menu, border_radius=25)
                pygame.draw.rect(screen, SUBTLE_GRAY, btn_menu, 2, border_radius=25)
                mm_text = font_ui.render("Main Menu", True, WHITE)
                screen.blit(mm_text, mm_text.get_rect(center=btn_menu.center))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()