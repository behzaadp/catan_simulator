from constants import PIPS

def evaluate_placements(board, player_color):
    """Algorithm 2: Rates the given player's initial placements."""
    user_nodes = [n for n in board.nodes if n.building == player_color]
    if len(user_nodes) < 2:
        return "Incomplete", 0, ["Finish placing all settlements to get a rating."]

    total_pips = 0
    resources_gathered = set()
    resource_pips = {"Lumber": 0, "Brick": 0, "Sheep": 0, "Wheat": 0, "Ore": 0}
    
    # 1. Calculate Raw Production and Resource Distribution
    for node in user_nodes:
        for hex_tile in node.hexes:
            if hex_tile.number:
                pip = PIPS.get(hex_tile.number, 0)
                total_pips += pip
                if hex_tile.resource != "Desert":
                    resources_gathered.add(hex_tile.resource)
                    resource_pips[hex_tile.resource] += pip

    feedback = []
    bonus_score = total_pips

    # 2. Evaluate Diversity
    if len(resources_gathered) == 5:
        feedback.append("Perfect resource diversity! You have access to everything.")
        bonus_score += 3
    elif len(resources_gathered) == 4:
        missing = list(set(["Lumber", "Brick", "Sheep", "Wheat", "Ore"]) - resources_gathered)[0]
        feedback.append(f"Good diversity. You are only missing {missing}.")
        bonus_score += 1
    else:
        feedback.append("Poor diversity. You will heavily rely on trading or ports.")
        bonus_score -= 2

    # 3. Evaluate Synergies
    if resource_pips["Lumber"] > 0 and resource_pips["Brick"] > 0:
        feedback.append("Strong road-building synergy (Lumber + Brick).")
        bonus_score += 2
    
    if resource_pips["Ore"] > 0 and resource_pips["Wheat"] > 0 and resource_pips["Sheep"] > 0:
        feedback.append("Excellent OWS synergy (Ore + Wheat + Sheep) for Cities/Dev Cards.")
        bonus_score += 3

    # 4. Check for Critical Flaws
    if resource_pips["Wheat"] == 0:
        feedback.append("CRITICAL: No Wheat. Wheat is required for both settlements and cities.")
        bonus_score -= 4
    if resource_pips["Ore"] == 0:
        feedback.append("WARNING: No Ore. Upgrading to cities will be difficult late game.")
        bonus_score -= 2

    # 5. Assign Grade based on adjusted score
    # A max theoretical raw pip count for 2 settlements is ~26. Average is ~18-20.
    if bonus_score >= 26:
        grade = "S (Masterful)"
    elif bonus_score >= 21:
        grade = "A (Great)"
    elif bonus_score >= 17:
        grade = "B (Good)"
    elif bonus_score >= 13:
        grade = "C (Playable)"
    else:
        grade = "D (Needs Improvement)"

    return grade, total_pips, feedback