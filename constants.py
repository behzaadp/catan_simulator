import pygame

# Screen
WIDTH, HEIGHT = 1000, 800
FPS = 60

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND = (173, 216, 230)  # Light blue for the ocean

# Player Colors
PLAYER_COLORS = [
    (255, 0, 0),    # Red (You)
    (0, 0, 255),    # Blue (Bot 1)
    (255, 165, 0),  # Orange (Bot 2)
    (255, 255, 255) # White (Bot 3)
]

# Resource Colors
COLORS = {
    "Wheat": (255, 223, 0),
    "Sheep": (144, 238, 144),
    "Lumber": (34, 139, 34),
    "Brick": (178, 34, 34),
    "Ore": (169, 169, 169),
    "Desert": (210, 180, 140)
}

# Catan Board Inventory
RESOURCES = (
    ["Lumber"] * 4 + ["Sheep"] * 4 + ["Wheat"] * 4 + 
    ["Brick"] * 3 + ["Ore"] * 3 + ["Desert"] * 1
)

TOKENS = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]

PORTS = (
    ["? 3:1"] * 4 + 
    ["Wheat 2:1", "Sheep 2:1", "Lumber 2:1", "Brick 2:1", "Ore 2:1"]
)

PIPS = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}

HEX_SIZE = 60