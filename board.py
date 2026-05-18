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
        self.building = None  # Will store player color

class Edge:
    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2
        self.hexes = []
        self.road = None      # Will store player color
        self.port = None      # Will store port type string

class Hexagon:
    def __init__(self, q, r, resource, number=None):
        self.q = q
        self.r = r
        self.resource = resource
        self.number = number
        self.x = WIDTH / 2 + HEX_SIZE * math.sqrt(3) * (q + r / 2)
        self.y = HEIGHT / 2 + HEX_SIZE * 3/2 * r
        self.corners = [] # Will be populated with Node objects

class Board:
    def __init__(self):
        self.hexes = []
        self.nodes = []
        self.edges = []
        self.generate_board()

    def _get_or_create_node(self, x, y):
        # Prevent duplicate intersections due to floating point math
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
        # Sort outer edges circularly to distribute ports evenly
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
        # Distance rule: No adjacent nodes can have a building
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

    def draw(self, surface, font, small_font):
        # Draw Hexes
        for hex_tile in self.hexes:
            vertices = [(n.x, n.y) for n in hex_tile.corners]
            pygame.draw.polygon(surface, COLORS[hex_tile.resource], vertices)
            pygame.draw.polygon(surface, BLACK, vertices, 2)
            
            if hex_tile.number:
                pygame.draw.circle(surface, WHITE, (int(hex_tile.x), int(hex_tile.y)), 20)
                pygame.draw.circle(surface, BLACK, (int(hex_tile.x), int(hex_tile.y)), 20, 1)
                num_color = (255, 0, 0) if hex_tile.number in [6, 8] else BLACK
                text = font.render(str(hex_tile.number), True, num_color)
                surface.blit(text, text.get_rect(center=(hex_tile.x, hex_tile.y - 5)))
                pip_text = small_font.render("." * PIPS[hex_tile.number], True, num_color)
                surface.blit(pip_text, pip_text.get_rect(center=(hex_tile.x, hex_tile.y + 10)))

        # Draw Ports, Roads, and Nodes
        for edge in self.edges:
            # Draw Port
            if edge.port:
                pygame.draw.line(surface, BLACK, (edge.node1.x, edge.node1.y), (edge.node2.x, edge.node2.y), 8)
                mx, my = (edge.node1.x + edge.node2.x) / 2, (edge.node1.y + edge.node2.y) / 2
                angle = math.atan2(my - HEIGHT/2, mx - WIDTH/2)
                tx, ty = mx + math.cos(angle) * 35, my + math.sin(angle) * 35
                
                pygame.draw.circle(surface, WHITE, (int(tx), int(ty)), 25)
                pygame.draw.circle(surface, BLACK, (int(tx), int(ty)), 25, 2)
                port_text = small_font.render(edge.port.split()[0], True, BLACK)
                surface.blit(port_text, port_text.get_rect(center=(tx, ty - 5)))
                
            # Draw Road
            if edge.road:
                pygame.draw.line(surface, edge.road, (edge.node1.x, edge.node1.y), (edge.node2.x, edge.node2.y), 10)

        # Draw Settlements
        for node in self.nodes:
            if node.building:
                pygame.draw.circle(surface, node.building, (int(node.x), int(node.y)), 12)
                pygame.draw.circle(surface, BLACK, (int(node.x), int(node.y)), 12, 2)