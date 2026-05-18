from constants import PIPS

def evaluate_placements(board, player_color):
    """Algorithm 2: Rates placements, port synergies, road trajectories, and number diversity."""
    user_nodes = [n for n in board.nodes if n.building == player_color]
    user_edges = [e for e in board.edges if e.road == player_color]
    
    if len(user_nodes) < 2 or len(user_edges) < 2:
        return "Incomplete", 0, ["Finish placing all settlements and roads."]

    total_pips = 0
    resources_gathered = set()
    numbers_gathered = set()
    resource_pips = {"Lumber": 0, "Brick": 0, "Sheep": 0, "Wheat": 0, "Ore": 0}
    owned_ports = []
    
    # 1. Base Production, Port Identification, and Number Tracking
    for node in user_nodes:
        for hex_tile in node.hexes:
            if hex_tile.number:
                pip = PIPS.get(hex_tile.number, 0)
                total_pips += pip
                numbers_gathered.add(hex_tile.number) 
                
                if hex_tile.resource != "Desert":
                    resources_gathered.add(hex_tile.resource)
                    resource_pips[hex_tile.resource] += pip
        
        for edge in node.edges:
            if edge.port and edge.port not in owned_ports:
                owned_ports.append(edge.port)

    feedback = []
    bonus_score = total_pips

    # 2. Evaluate Number Diversity
    num_diversity = len(numbers_gathered)
    if num_diversity >= 5:
        feedback.append(f"Excellent number diversity ({num_diversity} unique numbers). Very consistent rolls.")
        bonus_score += 3
    elif num_diversity == 4:
        feedback.append(f"Good number diversity ({num_diversity} unique numbers).")
        bonus_score += 1
    else:
        feedback.append(f"Poor number diversity ({num_diversity} unique numbers). Production will be very spiky.")
        bonus_score -= 2

    # 3. Evaluate Resource Diversity & Synergies
    if len(resources_gathered) == 5:
        feedback.append("Perfect diversity! Access to all 5 resources.")
        bonus_score += 3
    elif len(resources_gathered) == 4:
        missing = list(set(["Lumber", "Brick", "Sheep", "Wheat", "Ore"]) - resources_gathered)[0]
        feedback.append(f"Good diversity. Missing only {missing}.")
        bonus_score += 1
    else:
        bonus_score -= 2

    if resource_pips["Lumber"] > 0 and resource_pips["Brick"] > 0:
        feedback.append("Strong road-building synergy (Lumber + Brick).")
        bonus_score += 2
    if resource_pips["Ore"] > 0 and resource_pips["Wheat"] > 0 and resource_pips["Sheep"] > 0:
        feedback.append("Excellent OWS synergy (Ore/Wheat/Sheep) for late game.")
        bonus_score += 3
    if resource_pips["Wheat"] == 0:
        feedback.append("CRITICAL: No Wheat. Game will be very difficult.")
        bonus_score -= 4

    # 4. Evaluate Ports
    for port in owned_ports:
        if port == "? 3:1":
            feedback.append("Great flexibility with a starting 3:1 Port.")
            bonus_score += 2
        else:
            resource_type = port.split()[0]
            if resource_pips.get(resource_type, 0) >= 4:
                feedback.append(f"Massive Synergy! High {resource_type} production on a {resource_type} port.")
                bonus_score += 4
            elif resource_pips.get(resource_type, 0) == 0:
                feedback.append(f"Wasted Port: Started on a {resource_type} port but produce NO {resource_type}.")
                bonus_score -= 2
            else:
                feedback.append(f"Decent {resource_type} port setup, but needs more {resource_type} pips.")
                bonus_score += 1

    # 5. Evaluate Roads (Expansion Trajectory)
    for i, edge in enumerate(user_edges):
        target_node = None
        if edge.node1 in user_nodes and edge.node2 not in user_nodes:
            target_node = edge.node2
        elif edge.node2 in user_nodes and edge.node1 not in user_nodes:
            target_node = edge.node1
            
        if target_node:
            target_pips = sum([PIPS.get(h.number, 0) for h in target_node.hexes if h.number])
            target_has_port = any(e.port for e in target_node.edges)
            
            # Find how many paths we can take from this target node
            available_next_edges = [e for e in target_node.edges if e != edge and e.road is None]
            
            # Check for actual blockers
            if target_node.building is not None and target_node.building != player_color:
                feedback.append(f"Road {i+1} Warning: Blocked by an opponent's settlement!")
                bonus_score -= 2
            elif len(available_next_edges) == 0:
                feedback.append(f"Road {i+1} Warning: Points to a dead end with no further paths.")
                bonus_score -= 2
            elif target_has_port:
                feedback.append(f"Road {i+1} Trajectory: Excellent! Pointing towards a new port.")
                bonus_score += 2
            elif target_pips >= 8:
                feedback.append(f"Road {i+1} Trajectory: Strong! Points to high-yield hexes ({target_pips} pips).")
                bonus_score += 2
            elif target_pips <= 4:
                feedback.append(f"Road {i+1} Trajectory: Weak. Points to a low-yield zone ({target_pips} pips).")
                bonus_score -= 1

    # 6. Assign Grade
    if bonus_score >= 32:
        grade = "S+ (God Tier)"
    elif bonus_score >= 26:
        grade = "S (Masterful)"
    elif bonus_score >= 21:
        grade = "A (Great)"
    elif bonus_score >= 15:
        grade = "B (Good)"
    elif bonus_score >= 10:
        grade = "C (Playable)"
    else:
        grade = "D (Needs Improvement)"

    if len(feedback) > 9:
        feedback = feedback[:9]

    return grade, total_pips, feedback