import pygame
import random
import math
from constants import *

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hexes = []
        self.edges = []
        self.building = None  

class Edge:
    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2
        self.hexes = []
        self.road = None      
        self.port = None      

class Hexagon:
    def __init__(self, q, r, resource, number=None):
        self.q = q
        self.r = r
        self.resource = resource
        self.number = number
        self.x = WIDTH / 2 + HEX_SIZE * math.sqrt(3) * (q + r / 2)
        self.y = HEIGHT / 2 + HEX_SIZE * 3/2 * r
        self.corners = [] 

class Board:
    def __init__(self):
        self.hexes = []
        self.nodes = []
        self.edges = []
        # Initialize premium fonts for the board elements
        self.font_token = get_font(26, "token")
        self.font_port = get_font(13, "ui")
        self.generate_board()

    def _get_or_create_node(self, x, y):
        for n in self.nodes:
            if math.hypot(n.x - x, n.y - y) < 5:
                return n
        new_node = Node(x, y)
        self.nodes.append(new_node)
        return new_node

    def _get_or_create_edge(self, n1, n2):
        for e in self.edges:
            if (e.node1 == n1 and e.node2 == n2) or (e.node1 == n2 and e.node2 == n1):
                return e
        new_edge = Edge(n1, n2)
        n1.edges.append(new_edge)
        n2.edges.append(new_edge)
        self.edges.append(new_edge)
        return new_edge

    def generate_board(self):
        resources = list(RESOURCES)
        tokens = list(TOKENS)
        random.shuffle(resources)
        random.shuffle(tokens)

        # 1. Create Hexes
        for q in range(-2, 3):
            for r in range(-2, 3):
                if -2 <= q + r <= 2:
                    res = resources.pop()
                    num = tokens.pop() if res != "Desert" else None
                    self.hexes.append(Hexagon(q, r, res, num))

        # 2. Extract Graph (Nodes and Edges)
        for hex_tile in self.hexes:
            corners = []
            for i in range(6):
                angle_deg = 60 * i - 30
                angle_rad = math.pi / 180 * angle_deg
                vx = hex_tile.x + HEX_SIZE * math.cos(angle_rad)
                vy = hex_tile.y + HEX_SIZE * math.sin(angle_rad)
                node = self._get_or_create_node(vx, vy)
                if hex_tile not in node.hexes:
                    node.hexes.append(hex_tile)
                corners.append(node)
            hex_tile.corners = corners

            # Link corners with edges
            for i in range(6):
                n1 = corners[i]
                n2 = corners[(i + 1) % 6]
                edge = self._get_or_create_edge(n1, n2)
                if hex_tile not in edge.hexes:
                    edge.hexes.append(hex_tile)

        # 3. Assign Ports to Coastal Edges
        outer_edges = [e for e in self.edges if len(e.hexes) == 1]
        outer_edges.sort(key=lambda e: math.atan2(
            (e.node1.y + e.node2.y)/2 - HEIGHT/2, 
            (e.node1.x + e.node2.x)/2 - WIDTH/2
        ))
        
        shuffled_ports = list(PORTS)
        random.shuffle(shuffled_ports)
        step = len(outer_edges) / len(shuffled_ports)
        for i, port_type in enumerate(shuffled_ports):
            outer_edges[int(i * step)].port = port_type

    def is_valid_settlement(self, node):
        if node.building is not None:
            return False
        for edge in node.edges:
            neighbor = edge.node1 if edge.node2 == node else edge.node2
            if neighbor.building is not None:
                return False
        return True

    def is_valid_initial_road(self, edge, settlement_node):
        return edge.road is None and (edge.node1 == settlement_node or edge.node2 == settlement_node)

    def get_clicked_node(self, pos):
        for node in self.nodes:
            if math.hypot(node.x - pos[0], node.y - pos[1]) < 20:
                return node
        return None

    def get_clicked_edge(self, pos):
        for edge in self.edges:
            mx, my = (edge.node1.x + edge.node2.x) / 2, (edge.node1.y + edge.node2.y) / 2
            if math.hypot(mx - pos[0], my - pos[1]) < 20:
                return edge
        return None

    def draw(self, surface, font_large, font_small):
        # 1. DRAW UNIFIED ISLAND SHADOW
        board_shadow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for hex_tile in self.hexes:
            vertices = [(n.x, n.y) for n in hex_tile.corners]
            pygame.draw.polygon(board_shadow, SHADOW_COLOR, vertices)
        surface.blit(board_shadow, (0, SHADOW_OFFSET))

        # 2. DRAW HEXAGONS & TOKENS
        for hex_tile in self.hexes:
            vertices = [(n.x, n.y) for n in hex_tile.corners]
            base_color = COLORS[hex_tile.resource]
            
            # Base Fill
            pygame.draw.polygon(surface, base_color, vertices)
            
            # Inner Bevel/Border for depth
            darker_bevel = (max(base_color[0]-40, 0), max(base_color[1]-40, 0), max(base_color[2]-40, 0))
            pygame.draw.polygon(surface, darker_bevel, vertices, 3)
            
            # Number Token
            if hex_tile.number:
                tx, ty = int(hex_tile.x), int(hex_tile.y)
                
                # Token Base (Parchment color)
                pygame.draw.circle(surface, TOKEN_BG, (tx, ty), 20)
                pygame.draw.circle(surface, darker_bevel, (tx, ty), 20, 1)
                
                # Typography
                text_col = TOKEN_TEXT_CRIT if hex_tile.number in [6, 8] else TOKEN_TEXT_NORMAL
                text_surf = self.font_token.render(str(hex_tile.number), True, text_col)
                surface.blit(text_surf, text_surf.get_rect(center=(tx, ty - 3)))
                
                # Geometric Pips (Dots)
                pips_count = PIPS[hex_tile.number]
                pip_radius = 2.5
                pip_spacing = 7
                start_x = tx - ((pips_count - 1) * pip_spacing) / 2
                for i in range(pips_count):
                    px = int(start_x + i * pip_spacing)
                    py = int(ty + 12)
                    pygame.draw.circle(surface, text_col, (px, py), int(pip_radius))

        # 3. DRAW PORTS (Maritime Badges)
        for edge in self.edges:
            if edge.port:
                mx, my = (edge.node1.x + edge.node2.x) / 2, (edge.node1.y + edge.node2.y) / 2
                angle = math.atan2(my - HEIGHT/2, mx - WIDTH/2)
                
                # Push the badge out towards the water
                bx = mx + math.cos(angle) * 35
                by = my + math.sin(angle) * 35
                
                # Connector Dashed/Solid Line
                pygame.draw.line(surface, SUBTLE_GRAY, (mx, my), (bx, by), 3)
                
                # Badge Base
                pygame.draw.circle(surface, SHADOW_COLOR, (int(bx), int(by + SHADOW_OFFSET)), 18)
                pygame.draw.circle(surface, GLASS_BG_DARK, (int(bx), int(by)), 18)
                pygame.draw.circle(surface, WHITE, (int(bx), int(by)), 18, 2)
                
                # Badge Text
                port_type = edge.port.split()[0]
                display_text = "3:1" if port_type == "?" else port_type[:2].upper()
                p_color = COLORS.get(port_type, WHITE) if port_type != "?" else WHITE
                
                p_text = self.font_port.render(display_text, True, p_color)
                surface.blit(p_text, p_text.get_rect(center=(bx, by)))

        # 4. DRAW ROADS
        for edge in self.edges:
            if edge.road:
                # Road Casing (Outline)
                pygame.draw.line(surface, GLASS_BG_DARK, (edge.node1.x, edge.node1.y), (edge.node2.x, edge.node2.y), 10)
                # Road Core (Color)
                pygame.draw.line(surface, edge.road, (edge.node1.x, edge.node1.y), (edge.node2.x, edge.node2.y), 6)

        # 5. DRAW SETTLEMENTS (Geometric Houses)
        for node in self.nodes:
            if node.building:
                hx, hy = node.x, node.y
                size = 14
                
                # House Coordinates (Pentagon)
                house_verts = [
                    (hx - size*0.8, hy + size*0.8), # Bottom Left
                    (hx + size*0.8, hy + size*0.8), # Bottom Right
                    (hx + size*0.8, hy - size*0.2), # Top Right
                    (hx, hy - size*1.2),            # Roof Peak
                    (hx - size*0.8, hy - size*0.2)  # Top Left
                ]
                
                # Drop Shadow
                shadow_verts = [(vx, vy + SHADOW_OFFSET) for vx, vy in house_verts]
                pygame.draw.polygon(surface, SHADOW_COLOR, shadow_verts)
                
                # House Body
                pygame.draw.polygon(surface, node.building, house_verts)
                # House Border
                pygame.draw.polygon(surface, WHITE, house_verts, 2)