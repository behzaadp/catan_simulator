import pygame
import os

# --- CORE SETTINGS ---
WIDTH, HEIGHT = 1000, 800
FPS = 60
HEX_SIZE = 60

# --- NEW ART DIRECTION PALETTES ---

# Ocean Background (Will be drawn as a gradient)
OCEAN_BG_DARK = (15, 32, 39)
OCEAN_BG_LIGHT = (44, 83, 100)

# UI & Glassmorphism Colors
GLASS_BG_DARK = (30, 30, 35)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SUBTLE_GRAY = (200, 200, 200)

# Refined Player Colors (Slightly muted, premium tones)
PLAYER_COLORS = [
    (220, 53, 69),   # Red (You)
    (13, 110, 253),  # Blue (Bot 1)
    (253, 126, 20),  # Orange (Bot 2)
    (248, 249, 250)  # Off-White (Bot 3)
]

# Elevated Resource Colors (Organic, earthy tones)
COLORS = {
    "Wheat": (235, 186, 56),    # Goldenrod
    "Sheep": (143, 188, 143),   # Soft Sage
    "Lumber": (34, 110, 56),    # Deep Pine
    "Brick": (184, 76, 54),     # Terracotta
    "Ore": (112, 128, 144),     # Slate Gray
    "Desert": (210, 185, 145)   # Warm Sand
}

# Number Token Colors
TOKEN_BG = (245, 245, 240)       # Ivory/Parchment
TOKEN_TEXT_NORMAL = (40, 40, 45) # Anthracite Black
TOKEN_TEXT_CRIT = (200, 30, 30)  # Crimson Red for 6s and 8s

# Geometry & Shadows
SHADOW_OFFSET = 4
SHADOW_COLOR = (0, 0, 0, 80) # Black with alpha transparency

# --- UNTOUCHED CATAN LOGIC CONSTANTS ---
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

# --- TYPOGRAPHY ENGINE ---
def get_font(size, style="ui"):
    """
    Dynamically loads custom premium fonts. 
    Gracefully falls back to system fonts if .ttf files are missing.
    Must be called after pygame.init().
    """
    if style == "ui":
        try:
            # Modern, clean sans-serif for UI
            return pygame.font.Font("Montserrat-Bold.ttf", size)
        except FileNotFoundError:
            return pygame.font.SysFont("Segoe UI", size, bold=True)
            
    elif style == "token":
        try:
            # Bold serif for board tokens to mimic physical printed numbers
            return pygame.font.Font("RobotoSlab-Bold.ttf", size)
        except FileNotFoundError:
            return pygame.font.SysFont("Georgia", size, bold=True)