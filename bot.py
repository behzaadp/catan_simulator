import random
from constants import PIPS

def bot_get_best_settlement(board):
    best_nodes = []
    max_score = -1
    
    for node in board.nodes:
        if not board.is_valid_settlement(node):
            continue
        
        score = 0
        node_resources = {}
        
        # 1. Base raw production score
        for hex_tile in node.hexes:
            if hex_tile.number:
                pip = PIPS.get(hex_tile.number, 0)
                score += pip
                node_resources[hex_tile.resource] = node_resources.get(hex_tile.resource, 0) + pip
        
        # 2. Factor in Port placement
        for edge in node.edges:
            if edge.port:
                if edge.port == "? 3:1":
                    score += 2  # Flat bonus for flexible 3:1 port
                else:
                    port_res = edge.port.split()[0]
                    # If the bot is producing the resource of the port, it's highly valuable
                    if node_resources.get(port_res, 0) > 0:
                        score += 4 
                    else:
                        score += 1 # Minor bonus just for having a specific port
        
        if score > max_score:
            max_score = score
            best_nodes = [node]
        elif score == max_score:
            best_nodes.append(node)
            
    return random.choice(best_nodes) if best_nodes else None


def bot_get_best_road(board, settlement_node):
    best_edges = []
    max_score = -1
    
    for edge in settlement_node.edges:
        if edge.road is not None:
            continue
            
        other_node = edge.node1 if edge.node2 == settlement_node else edge.node2
        score = 0
        
        # 1. Check raw production of target node
        for hex_tile in other_node.hexes:
            if hex_tile.number:
                score += PIPS.get(hex_tile.number, 0)
                
        # 2. Strongly prefer moving towards a port
        target_has_port = any(e.port for e in other_node.edges)
        if target_has_port:
            score += 3
            
        if score > max_score:
            max_score = score
            best_edges = [edge]
        elif score == max_score:
            best_edges.append(edge)
            
    return random.choice(best_edges) if best_edges else None