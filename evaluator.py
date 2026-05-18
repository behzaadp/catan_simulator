from constants import PIPS

def evaluate_placements(board, player_color):
    """Algorithm 2: Rates placements, port synergies, and road trajectories."""
    user_nodes = [n for n in board.nodes if n.building == player_color]
    user_edges = [e for e in board.edges if e.road == player_color]
    
    if len(user_nodes) < 2 or len(user_edges) < 2:
        return "Incomplete", 0, ["Finish placing all settlements and roads."]

    total_pips = 0
    resources_gathered = set()
    resource_pips = {"Lumber": 0, "Brick": 0, "Sheep": 0, "Wheat": 0, "Ore": 0}
    owned_ports = []
    
    # 1. Base Production & Port Identification
    for node in user_nodes:
        for hex_tile in node.hexes:
            if hex_tile.number:
                pip = PIPS.get(hex_tile.number, 0)
                total_pips += pip
                if hex_tile.resource != "Desert":
                    resources_gathered.add(hex_tile.resource)
                    resource_pips[hex_tile.resource] += pip
        
        # Check if the settlement itself sits directly on a port
        for edge in node.edges:
            if edge.port:
                if edge.port not in owned_ports: # Prevent double counting
                    owned_ports.append(edge.port)

    feedback = []
    bonus_score = total_pips

    # 2. Evaluate Diversity & Synergies
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

    # 3. Evaluate Ports
    for port in owned_ports:
        if port == "? 3:1":
            feedback.append("Great flexibility with a starting 3:1 Port.")
            bonus_score += 2
        else:
            resource_type = port.split()[0]  # Extracts "Wheat" from "Wheat 2:1"
            if resource_pips.get(resource_type, 0) >= 4:
                feedback.append(f"Massive Synergy! High {resource_type} production on a {resource_type} port.")
                bonus_score += 4
            elif resource_pips.get(resource_type, 0) == 0:
                feedback.append(f"Wasted Port: You started on a {resource_type} port but produce NO {resource_type}.")
                bonus_score -= 2
            else:
                feedback.append(f"Decent {resource_type} port setup, but needs more {resource_type} pips.")
                bonus_score += 1

    # 4. Evaluate Roads (Expansion Trajectory)
    for i, edge in enumerate(user_edges):
        # Identify the node the road points towards (the node without the settlement)
        target_node = None
        if edge.node1 in user_nodes and edge.node2 not in user_nodes:
            target_node = edge.node2
        elif edge.node2 in user_nodes and edge.node1 not in user_nodes:
            target_node = edge.node1
            
        if target_node:
            # Calculate potential of the target expansion node
            target_pips = sum([PIPS.get(h.number, 0) for h in target_node.hexes if h.number])
            target_has_port = any(e.port for e in target_node.edges)
            
            # Distance rule check: Did you point your road directly into an enemy settlement?
            if not board.is_valid_settlement(target_node):
                feedback.append(f"Road {i+1} Warning: Points to an invalid/blocked intersection!")
                bonus_score -= 2
            elif target_has_port:
                feedback.append(f"Road {i+1} Trajectory: Excellent! Pointing directly towards a new port.")
                bonus_score += 2
            elif target_pips >= 8: # 8 pips is a solid 3-hex intersection
                feedback.append(f"Road {i+1} Trajectory: Strong! Points to a high-yield spot ({target_pips} pips).")
                bonus_score += 2
            elif target_pips <= 4:
                feedback.append(f"Road {i+1} Trajectory: Weak. Points to a low-yield dead zone ({target_pips} pips).")
                bonus_score -= 1

    # 5. Assign Grade (Adjusted thresholds for the new bonuses)
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

    # Slice feedback so it doesn't overflow the UI screen
    if len(feedback) > 7:
        feedback = feedback[:7]

    return grade, total_pips, feedback