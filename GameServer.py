import threading
import pygame
import socket
import sys
import random
import os
from game_state import GameState

# Initialize global variables
posx = 300
posy = 200
game_state = GameState()
client_connected = False


def play_sound(sound_file):
    """Play a sound effect if the file exists"""
    if os.path.exists(sound_file):
        sound = pygame.mixer.Sound(sound_file)
        sound.play()

def draw_text(screen, text, size, x, y, color=(255, 255, 255)):
    """Helper function to draw text on screen"""
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    screen.blit(text_surface, text_rect)

def draw_menu(screen, screen_width, screen_height):
    """Draw the game menu"""
    screen.fill((0, 0, 50))  # Dark blue background
    
    # Draw game title
    draw_text(screen, "BUCKET CATCH", 64, screen_width // 2, screen_height // 4, (255, 255, 0))
    
    # Draw menu options
    draw_text(screen, "PLAY", 36, screen_width // 2, screen_height // 2, (255, 255, 255))
    draw_text(screen, "QUIT", 36, screen_width // 2, screen_height // 2 + 50, (255, 255, 255))
    
    # Draw selection indicator (will later be made interactive)
    pygame.draw.rect(screen, (255, 0, 0), (screen_width // 2 - 60, screen_height // 2, 10, 10))
    
    # Draw connection status
    status_text = "Client Connected" if client_connected else "Waiting for Client..."
    status_color = (0, 255, 0) if client_connected else (255, 165, 0)
    draw_text(screen, status_text, 24, screen_width // 2, screen_height - 100, status_color)
    
    # Draw instructions
    draw_text(screen, "Press SPACE to start", 20, screen_width // 2, screen_height - 50)

def draw_game_over(screen, screen_width, screen_height, score):
    """Draw the game over screen"""
    screen.fill((50, 0, 0))  # Dark red background
    
    draw_text(screen, "GAME OVER", 64, screen_width // 2, screen_height // 4, (255, 255, 0))
    draw_text(screen, f"SCORE: {score}", 36, screen_width // 2, screen_height // 2)
    draw_text(screen, "Press SPACE to play again", 24, screen_width // 2, screen_height - 100)
    draw_text(screen, "Press ESC to quit", 24, screen_width // 2, screen_height - 70)


def draw_stats_background(screen, x, y, width, height, color):
    """Draw a semi-transparent background for stats text"""
    # Create a surface with per-pixel alpha
    s = pygame.Surface((width, height), pygame.SRCALPHA)
    # Fill with the given color and alpha
    s.fill(color)
    # Blit the surface onto the screen
    screen.blit(s, (x, y))

def draw_minecraft_text(screen, text, size, x, y, color=(255, 255, 255)):
    """Draw text using the Minecraft font"""
    # Check if the Minecraft font is already loaded
    if not hasattr(draw_minecraft_text, 'minecraft_font'):
        try:
            # Try to load the Minecraft font
            font_path = os.path.join("fonts", "Minecraft.ttf")
            draw_minecraft_text.minecraft_font = {}
            pygame.font.init()
        except Exception as e:
            print(f"Could not initialize font system: {e}")
            draw_minecraft_text.minecraft_font = None
    
    # Try to get or create the font at the requested size
    if draw_minecraft_text.minecraft_font is not None:
        if size not in draw_minecraft_text.minecraft_font:
            try:
                font_path = os.path.join("fonts", "Minecraft.ttf")
                draw_minecraft_text.minecraft_font[size] = pygame.font.Font(font_path, size)
            except Exception as e:
                print(f"Could not load Minecraft font at size {size}: {e}")
                # Fall back to system font
                draw_minecraft_text.minecraft_font[size] = pygame.font.SysFont(None, size)
        
        # Create the text surface
        font = draw_minecraft_text.minecraft_font[size]
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        screen.blit(text_surface, text_rect)
    else:
        # Fall back to the original draw_text function
        draw_text(screen, text, size, x, y, color)

def GameThread():
    """Main game thread handling rendering and game logic"""
    pygame.init()
    pygame.mixer.init()  # Initialize sound mixer
    
    screen_width, screen_height = 600, 400
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Minecraft Chicken Jockey Catch")

    clock = pygame.time.Clock()

    # Get global variables
    global posx, posy, game_state, client_connected
    
    # Import custom classes
    from ball import Ball
    from bucket import Bucket
    
    # Create game objects with custom Minecraft images
    ball = Ball(screen_width, screen_height, "images/chicken_jockey.png", width=40, height=60)
    bucket = Bucket(screen_width, screen_height, "images/lava_bucket.png", width=80, height=80)
    
    # Load background image
    background = None
    try:
        background = pygame.image.load("images/minecraft_forest.png").convert()
        background = pygame.transform.scale(background, (screen_width, screen_height))
    except pygame.error as e:
        print(f"Could not load background image: {e}")
    
    # Set initial position
    posx = bucket.x
    posy = bucket.y
    
    # Load sound effects
    catch_sound = "sounds/catch.wav"
    miss_sound = "sounds/miss.wav"
    
    # Menu selection
    menu_selection = 0  # 0 = Play, 1 = Quit
    
    # Track previous state
    prev_state = game_state.get_state()
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                # Menu state
                if game_state.get_state() == GameState.MENU:
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        menu_selection = 1 - menu_selection
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        if menu_selection == 0:  # Play selected
                            game_state.set_state(GameState.PLAYING)
                            game_state.reset_game()
                            ball.reset()
                            bucket.x = screen_width // 2 - bucket.width // 2
                            bucket.y = screen_height - 100
                            posx = bucket.x
                            posy = bucket.y
                        else:  # Quit selected
                            running = False
                
                # Game over state
                elif game_state.get_state() == GameState.GAME_OVER:
                    if event.key == pygame.K_SPACE:
                        game_state.set_state(GameState.PLAYING)
                        game_state.reset_game()
                        ball.reset()
                        bucket.x = screen_width // 2 - bucket.width // 2
                        bucket.y = screen_height - 100
                        posx = bucket.x
                        posy = bucket.y
                    elif event.key == pygame.K_ESCAPE:
                        game_state.set_state(GameState.MENU)
        
        # Get current state
        current_state = game_state.get_state()
        
        # Check for state transitions - critical for reset synchronization
        if current_state != prev_state:
            print(f"Game state changed: {prev_state} → {current_state}")
            
            # When entering PLAYING state, always reset
            if current_state == GameState.PLAYING:
                print("Resetting ball and bucket positions")
                ball.reset()
                bucket.x = screen_width // 2 - bucket.width // 2
                bucket.y = screen_height - 100
                posx = bucket.x
                posy = bucket.y
        
        # Menu state
        if current_state == GameState.MENU:
            # Menu background and UI
            try:
                if not hasattr(GameThread, 'menu_bg'):
                    GameThread.menu_bg = pygame.image.load("images/minecraft_kitten.png").convert()
                    GameThread.menu_bg = pygame.transform.scale(GameThread.menu_bg, (screen_width, screen_height))
                screen.blit(GameThread.menu_bg, (0, 0))
            except (pygame.error, AttributeError) as e:
                print(f"Menu background load error: {e}")
                screen.fill((14, 23, 48))
            
            # Overlay for text readability
            draw_stats_background(screen, 0, 0, screen_width, screen_height, (0, 0, 0, 160))
            
            # Menu text
            draw_minecraft_text(screen, "CHICKEN JOCKEY CATCH", 36, screen_width // 2, screen_height // 4, (255, 215, 0))
            draw_minecraft_text(screen, "PLAY", 24, screen_width // 2, screen_height // 2, (255, 255, 255))
            draw_minecraft_text(screen, "QUIT", 24, screen_width // 2, screen_height // 2 + 50, (255, 255, 255))
            
            # Selection indicator
            pygame.draw.rect(screen, (255, 0, 0), 
                           (screen_width // 2 - 60, 
                            screen_height // 2 + (50 * menu_selection), 10, 10))
            
            # Connection status
            status_text = "Client Connected" if client_connected else "Waiting for Client..."
            status_color = (0, 255, 0) if client_connected else (255, 165, 0)
            draw_minecraft_text(screen, status_text, 18, screen_width // 2, screen_height - 100, status_color)
            draw_minecraft_text(screen, "Press SPACE to start", 16, screen_width // 2, screen_height - 50)
        
        # Playing state
        elif current_state == GameState.PLAYING:
            # Update game objects
            bucket.update(posx, posy)
            ball.update(game_state)

            # Collision detection
            if bucket.collides_with(ball.get_rect()):
                game_state.score += 1
                play_sound(catch_sound)
                
                # Increase difficulty
                if game_state.score % 5 == 0:
                    game_state.increase_difficulty()
                
                # Reset ball after catch
                ball.reset()
            elif ball.is_off_screen():
                # Game over when ball is missed
                play_sound(miss_sound)
                game_state.set_state(GameState.GAME_OVER)
                ball.y = screen_height + 100  # Ensure ball is off-screen
            
            # Draw game world
            if background:
                screen.blit(background, (0, 0))
            else:
                screen.fill((115, 185, 255))
            
            # Draw game objects
            bucket.draw(screen)
            ball.draw(screen)
            
            # Draw UI elements
            draw_stats_background(screen, 10, 5, 130, 30, (0, 0, 0, 128))
            draw_minecraft_text(screen, f"Level: {game_state.difficulty_level}", 18, 70, 10, (255, 255, 255))
            
            draw_stats_background(screen, screen_width - 140, 5, 130, 30, (0, 0, 0, 128))
            draw_minecraft_text(screen, f"Score: {game_state.score}", 18, screen_width - 70, 10, (255, 255, 255))
        
        # Game over state
        elif current_state == GameState.GAME_OVER:
            # Game over screen
            screen.fill((89, 16, 16))
            
            draw_minecraft_text(screen, "GAME OVER", 48, screen_width // 2, screen_height // 4, (255, 255, 0))
            draw_minecraft_text(screen, f"SCORE: {game_state.score}", 32, screen_width // 2, screen_height // 2)
            draw_minecraft_text(screen, "Press SPACE to play again", 20, screen_width // 2, screen_height - 100)
            draw_minecraft_text(screen, "Press ESC to quit", 20, screen_width // 2, screen_height - 70)
        
        # Store previous state for next frame
        prev_state = current_state
        
        pygame.display.update()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()


def ServerThread():
    """Network server thread handling client connections"""
    global posx, posy, game_state, client_connected
    
    # Get server IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        host = s.getsockname()[0]
    except:
        host = "127.0.0.1"  # Fallback to localhost
    finally:
        s.close()
    
    print(f"Server IP: {host}")
    port = 5000

    server_socket = socket.socket()
    server_socket.bind((host, port))
    print("Server enabled...")
    server_socket.listen(2)
    
    # Set dimensions for screen boundaries
    screen_width, screen_height = 600, 400
    bucket_width, bucket_height = 80, 80
    
    while True:
        try:
            conn, address = server_socket.accept()
            print("Connection from: " + str(address))
            client_connected = True
            
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    break
                
                print(f"Command received: {data} | Current state: {game_state.get_state()}")
                
                # Handle movement commands
                if game_state.get_state() == GameState.PLAYING:
                    # Calculate movement speed based on difficulty
                    move_speed = 10 * (1 + (game_state.difficulty_level * 0.1))
                    
                    if data == 'a':
                        posx -= move_speed
                        if posx < 0:
                            posx = 0
                    if data == 'd':
                        posx += move_speed
                        if posx > screen_width - bucket_width:
                            posx = screen_width - bucket_width
                
                # Handle game control commands
                if data == 'space':
                    print(f"SPACE command received in state {game_state.get_state()}")
                    
                    # Direct state changes based on current state
                    if game_state.get_state() == GameState.MENU or game_state.get_state() == GameState.GAME_OVER:
                        # Reset everything in one place
                        game_state.set_state(GameState.PLAYING)
                        game_state.reset_game()
                        # Reset position
                        posx = (screen_width - bucket_width) // 2
                        posy = screen_height - 100
                        print(f"Game started/restarted via client command")
                        
                elif data == 'esc' and game_state.get_state() == GameState.GAME_OVER:
                    game_state.set_state(GameState.MENU)
                    print("Returned to menu via client command")
            
            client_connected = False
            conn.close()
        except Exception as e:
            print(f"Server error: {e}")
            client_connected = False

if __name__ == "__main__":
    # Create sounds directory if it doesn't exist
    if not os.path.exists("sounds"):
        os.makedirs("sounds")
        print("Created sounds directory. Please add sound files.")
    
    # Start game threads
    t1 = threading.Thread(target=GameThread, args=[])
    t2 = threading.Thread(target=ServerThread, args=[])
    t1.start()
    t2.start()