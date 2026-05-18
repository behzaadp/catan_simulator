import random
from constants import PIPS

def bot_get_best_settlement(board):
    best_nodes = []
    max_score = -1
    
    for node in board.nodes:
        if not board.is_valid_settlement(node):
            continue
        
        # Calculate score based on adjacent hex probabilities
        score = 0
        for hex_tile in node.hexes:
            if hex_tile.number:
                score += PIPS.get(hex_tile.number, 0)
        
        if score > max_score:
            max_score = score
            best_nodes = [node]
        elif score == max_score:
            best_nodes.append(node)
            
    # Randomly pick among tied "best" spots to keep games varied
    return random.choice(best_nodes) if best_nodes else None

def bot_get_best_road(board, settlement_node):
    best_edges = []
    max_score = -1
    
    for edge in settlement_node.edges:
        if edge.road is not None:
            continue
            
        # Look at the node on the other side of this edge to judge value
        other_node = edge.node1 if edge.node2 == settlement_node else edge.node2
        score = 0
        for hex_tile in other_node.hexes:
            if hex_tile.number:
                score += PIPS.get(hex_tile.number, 0)
                
        if score > max_score:
            max_score = score
            best_edges = [edge]
        elif score == max_score:
            best_edges.append(edge)
            
    return random.choice(best_edges) if best_edges else None