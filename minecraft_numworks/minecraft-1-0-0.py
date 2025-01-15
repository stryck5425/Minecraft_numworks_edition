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
        kandinsky.draw_string(f"Launcher: "+ VERSION, 10, 120)
        kandinsky.draw_string(f"Assets: "+ mc_assets.VERSION, 10, 140)
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