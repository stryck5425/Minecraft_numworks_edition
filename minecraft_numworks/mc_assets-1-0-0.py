# mc_assets.py
"""
MC Assets - Version 1.0.0
Contains game assets, textures and core functions for 2D Minecraft
"""
import kandinsky
import ion
import random
import time

VERSION = "1.0.0"

# Constants
TILE_SIZE = 16
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 222
GRAVITY = 1
JUMP_FORCE = -8
CHUNK_SIZE = SCREEN_WIDTH // TILE_SIZE

# Colors
COLORS = {
    'sky': (135, 206, 235),
    'grass_top': (34, 139, 34),
    'grass_side': (25, 110, 25),
    'dirt': (139, 69, 19),
    'dirt_dark': (120, 60, 16),
    'wood': (160, 82, 45),
    'wood_dark': (140, 70, 35),
    'leaves': (34, 139, 34),
    'leaves_dark': (25, 110, 25),
    'stone': (128, 128, 128),
    'stone_dark': (100, 100, 100)
}

class Block:
    def __init__(self, x, y, block_type):
        self.x = int(x)
        self.y = int(y)
        self.type = block_type
        self.solid = block_type in ['grass', 'dirt', 'stone']

    def draw(self):
        if self.type == 'grass':
            kandinsky.fill_rect(self.x, self.y, TILE_SIZE, TILE_SIZE, COLORS['dirt'])
            kandinsky.fill_rect(self.x, self.y, TILE_SIZE, TILE_SIZE//4, COLORS['grass_top'])
            for _ in range(3):
                dx = random.randint(0, TILE_SIZE-4)
                dy = random.randint(TILE_SIZE//4, TILE_SIZE-4)
                kandinsky.fill_rect(self.x + dx, self.y + dy, 4, 4, COLORS['dirt_dark'])
        elif self.type == 'dirt':
            kandinsky.fill_rect(self.x, self.y, TILE_SIZE, TILE_SIZE, COLORS['dirt'])
            for _ in range(4):
                dx = random.randint(0, TILE_SIZE-4)
                dy = random.randint(0, TILE_SIZE-4)
                kandinsky.fill_rect(self.x + dx, self.y + dy, 4, 4, COLORS['dirt_dark'])
        elif self.type == 'stone':
            kandinsky.fill_rect(self.x, self.y, TILE_SIZE, TILE_SIZE, COLORS['stone'])
            for _ in range(3):
                dx = random.randint(0, TILE_SIZE-4)
                dy = random.randint(0, TILE_SIZE-4)
                kandinsky.fill_rect(self.x + dx, self.y + dy, 4, 4, COLORS['stone_dark'])
        elif self.type == 'wood':
            kandinsky.fill_rect(self.x, self.y, TILE_SIZE, TILE_SIZE, COLORS['wood'])
            kandinsky.fill_rect(self.x + TILE_SIZE//4, self.y, TILE_SIZE//2, TILE_SIZE, COLORS['wood_dark'])
        elif self.type == 'leaves':
            kandinsky.fill_rect(self.x, self.y, TILE_SIZE, TILE_SIZE, COLORS['leaves'])
            for _ in range(3):
                dx = random.randint(0, TILE_SIZE-4)
                dy = random.randint(0, TILE_SIZE-4)
                kandinsky.fill_rect(self.x + dx, self.y + dy, 4, 4, COLORS['leaves_dark'])

class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = 0
        self.width = TILE_SIZE - 2
        self.height = TILE_SIZE * 2
        self.vel_y = 0
        self.speed = 4
        self.jumping = False
        
    def draw(self):
        # Body
        kandinsky.fill_rect(
            int(self.x), 
            int(self.y + self.height//2), 
            self.width, 
            self.height//2, 
            (0, 0, 255)
        )
        # Head
        kandinsky.fill_rect(
            int(self.x + 2), 
            int(self.y), 
            self.width - 4, 
            self.height//2, 
            (255, 200, 150)
        )
        # Eyes
        kandinsky.fill_rect(
            int(self.x + 4), 
            int(self.y + 6), 
            2, 
            2, 
            (0, 0, 0)
        )
        kandinsky.fill_rect(
            int(self.x + self.width - 6), 
            int(self.y + 6), 
            2, 
            2, 
            (0, 0, 0)
        )
        
    def move(self, dx, blocks):
        new_x = self.x + dx
        
        # World wrapping
        if new_x < 0:
            new_x = SCREEN_WIDTH - self.width
        elif new_x + self.width > SCREEN_WIDTH:
            new_x = 0
            
        can_move = True
        for block in blocks:
            if block.solid:
                if (new_x < block.x + TILE_SIZE and
                    new_x + self.width > block.x and
                    int(self.y) < block.y + TILE_SIZE and
                    int(self.y) + self.height > block.y):
                    can_move = False
                    break
        
        if can_move:
            self.x = new_x
                    
    def apply_gravity(self, blocks):
        self.vel_y += GRAVITY
        new_y = int(self.y + self.vel_y)
        
        for block in blocks:
            if block.solid and self.collides_with_pos(self.x, new_y, block):
                if self.vel_y > 0:  # Falling
                    new_y = block.y - self.height
                    self.vel_y = 0
                    self.jumping = False
                elif self.vel_y < 0:  # Jumping
                    new_y = block.y + TILE_SIZE
                    self.vel_y = 0
        
        self.y = new_y
        
    def jump(self):
        if not self.jumping:
            self.vel_y = JUMP_FORCE
            self.jumping = True
            
    def collides_with_pos(self, test_x, test_y, block):
        return (int(test_x) < block.x + TILE_SIZE and
                int(test_x) + self.width > block.x and
                int(test_y) < block.y + TILE_SIZE and
                int(test_y) + self.height > block.y)
                
    def collides_with(self, block):
        return self.collides_with_pos(self.x, self.y, block)

def generate_terrain(start_x, width, prev_height=None):
    blocks = []
    heights = []
    base_height = SCREEN_HEIGHT // TILE_SIZE // 2
    
    if prev_height is not None:
        heights.append(prev_height)
    else:
        heights.append(base_height)
    
    for x in range(1, width + 1):
        diff = random.randint(-1, 1)
        height = max(5, min(base_height + diff, SCREEN_HEIGHT // TILE_SIZE - 8))
        heights.append(height)
        heights[x] = (heights[x] + heights[x-1]) // 2
    
    for x in range(width):
        block_x = (start_x + x) * TILE_SIZE
        height = heights[x]
        
        if block_x >= SCREEN_WIDTH:
            block_x = block_x % SCREEN_WIDTH
            
        blocks.append(Block(block_x, height * TILE_SIZE, 'grass'))
        
        for y in range(height + 1, height + 5):
            blocks.append(Block(block_x, y * TILE_SIZE, 'dirt'))
        for y in range(height + 5, SCREEN_HEIGHT // TILE_SIZE):
            blocks.append(Block(block_x, y * TILE_SIZE, 'stone'))
            
        if random.random() < 0.1 and x > 2 and x < width-3:
            if abs(heights[x-1] - heights[x]) <= 1 and abs(heights[x+1] - heights[x]) <= 1:
                tree_height = random.randint(3, 5)
                for y in range(1, tree_height):
                    blocks.append(Block(block_x, (height-y) * TILE_SIZE, 'wood'))
                for lx in range(-2, 3):
                    for ly in range(-3, 0):
                        if abs(lx) + abs(ly) <= 3:
                            leaf_x = (block_x + lx * TILE_SIZE) % SCREEN_WIDTH
                            leaf_y = (height - tree_height + ly) * TILE_SIZE
                            blocks.append(Block(leaf_x, leaf_y, 'leaves'))
    
    return blocks, heights[-1]

def draw_sky():
    kandinsky.fill_rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, COLORS['sky'])

def handle_input(player, blocks):
    if ion.keydown(ion.KEY_LEFT):
        player.move(-player.speed, blocks)
    if ion.keydown(ion.KEY_RIGHT):
        player.move(player.speed, blocks)
    if ion.keydown(ion.KEY_UP):
        player.jump()

# minecraft.py
"""
Minecraft 2D Launcher - Version 1.0.0
Main game launcher for 2D Minecraft
"""
import mc_assets
import kandinsky
import time

VERSION = "1.0.0"

def check_version():
    if VERSION != mc_assets.VERSION:
        kandinsky.fill_rect(0, 0, 320, 222, (255, 255, 255))
        kandinsky.draw_string("Version mismatch!", 10, 100)
        kandinsky.draw_string(f"Launcher: {VERSION}", 10, 120)
        kandinsky.draw_string(f"Assets: {mc_assets.VERSION}", 10, 140)
        time.sleep(3)
        return False
    return True

def main():
    if not check_version():
        return
        
    # Initialize game
    mc_assets.draw_sky()
    blocks, last_height = mc_assets.generate_terrain(
        start_x=0, 
        width=mc_assets.SCREEN_WIDTH // mc_assets.TILE_SIZE
    )
    player = mc_assets.Player()
    
    # Initial draw
    for block in blocks:
        block.draw()
    player.draw()
    
    # Game loop
    last_pos = (player.x, player.y)
    while True:
        # Handle input
        mc_assets.handle_input(player, blocks)
        
        # Apply gravity
        player.apply_gravity(blocks)
        
        # Only redraw if position changed
        current_pos = (player.x, player.y)
        if current_pos != last_pos:
            # Clear old position
            kandinsky.fill_rect(int(last_pos[0]), int(last_pos[1]), 
                              player.width, player.height, mc_assets.COLORS['sky'])
            
            # Redraw blocks that might have been covered
            for block in blocks:
                if (block.x < last_pos[0] + player.width and 
                    block.x + mc_assets.TILE_SIZE > last_pos[0] and
                    block.y < last_pos[1] + player.height and 
                    block.y + mc_assets.TILE_SIZE > last_pos[1]):
                    block.draw()
            
            # Draw player at new position
            player.draw()
            last_pos = current_pos
        
        # Small delay to control game speed
        time.sleep(0.03)

main()