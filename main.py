import pygame
import sys
import random
from constants import *
from menu import Menu
from board import Board
from bot import bot_get_best_settlement, bot_get_best_road
from evaluator import evaluate_placements # IMPORT ALGORITHM 2

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Catan Placement Simulator")
    clock = pygame.time.Clock()

    font_large = pygame.font.SysFont("Arial", 24, bold=True)
    font_small = pygame.font.SysFont("Arial", 16, bold=True)
    font_ui = pygame.font.SysFont("Arial", 28, bold=True)

    state = "MENU"
    menu = Menu()
    board = None
    
    players = []
    draft_sequence = []
    current_turn_index = 0
    phase = "SETTLEMENT"
    last_placed_node = None

    # End Game Buttons
    btn_play_again = pygame.Rect(WIDTH - 220, 20, 200, 50)
    btn_menu = pygame.Rect(WIDTH - 220, 80, 200, 50)

    running = True
    while running:
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
                        if btn_play_again.collidepoint(event.pos):
                            random.shuffle(players)
                            draft_sequence = list(range(len(players))) + list(range(len(players) - 1, -1, -1))
                            current_turn_index = 0
                            phase = "SETTLEMENT"
                            last_placed_node = None
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

        if state == "MENU":
            menu.draw(screen)
        elif state == "GAME":
            screen.fill(BACKGROUND)
            board.draw(screen, font_large, font_small)
            
            if phase != "FINISHED":
                current_player = players[draft_sequence[current_turn_index]]
                order_names = [p["name"] for p in players]
                order_text = font_ui.render(f"Draft Order: {', '.join(order_names)}", True, BLACK)
                screen.blit(order_text, (20, 20))

                prompt = "Place a Settlement!" if phase == "SETTLEMENT" else "Place a Road!"
                action_text = font_ui.render(f"{current_player['name']}'s Turn: {prompt}", True, current_player["color"])
                shadow = font_ui.render(f"{current_player['name']}'s Turn: {prompt}", True, BLACK)
                screen.blit(shadow, (21, 61))
                screen.blit(action_text, (20, 60))
            
            else:
                # --- EVALUATION UI PANEL ---
                grade, pips, feedback = evaluate_placements(board, PLAYER_COLORS[0])
                
                panel_rect = pygame.Rect(20, HEIGHT - 220, WIDTH - 40, 200)
                pygame.draw.rect(screen, (240, 240, 240), panel_rect, border_radius=10)
                pygame.draw.rect(screen, BLACK, panel_rect, 3, border_radius=10)
                
                title_text = font_ui.render(f"Placement Evaluation - Grade: {grade}", True, PLAYER_COLORS[0])
                screen.blit(title_text, (40, HEIGHT - 200))
                
                pip_text = font_large.render(f"Total Raw Production (Pips): {pips}", True, BLACK)
                screen.blit(pip_text, (40, HEIGHT - 160))
                
                for i, fb in enumerate(feedback):
                    fb_text = font_small.render(f"• {fb}", True, (50, 50, 50))
                    screen.blit(fb_text, (40, HEIGHT - 120 + (i * 25)))

                # Draw Buttons
                pygame.draw.rect(screen, WHITE, btn_play_again)
                pygame.draw.rect(screen, BLACK, btn_play_again, 3)
                pa_text = font_large.render("Play Again", True, BLACK)
                screen.blit(pa_text, pa_text.get_rect(center=btn_play_again.center))

                pygame.draw.rect(screen, WHITE, btn_menu)
                pygame.draw.rect(screen, BLACK, btn_menu, 3)
                mm_text = font_large.render("Main Menu", True, BLACK)
                screen.blit(mm_text, mm_text.get_rect(center=btn_menu.center))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()