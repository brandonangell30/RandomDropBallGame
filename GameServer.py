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

def GameThread():
    """Main game thread handling rendering and game logic"""
    pygame.init()
    pygame.mixer.init()  # Initialize sound mixer
    
    screen_width, screen_height = 600, 400
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Bucket Catch Game")

    clock = pygame.time.Clock()

    # Get global variables
    global posx, posy, game_state, client_connected
    
    # Set initial position
    posx = screen_width // 2 - 40  # Center the bucket
    posy = screen_height - 40  # Fixed bucket Y position

    # Game objects
    bucket_width = 80
    bucket_height = 20
    bucket_color = (0, 51, 204)
    bucket_outline_color = (0, 0, 255)

    object_width = 20
    object_height = 20
    object_color = (255, 0, 0)
    
    base_object_speed = 3
    object_speed = base_object_speed
    
    object_x = random.randint(0, screen_width - object_width)
    object_y = 0
    
    # Load sound effects (these files would need to be created or downloaded)
    catch_sound = "sounds/catch.wav"
    miss_sound = "sounds/miss.wav"
    
    # Menu selection
    menu_selection = 0  # 0 = Play, 1 = Quit
    
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
                        # Toggle between Play and Quit
                        menu_selection = 1 - menu_selection
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        if menu_selection == 0:  # Play selected
                            game_state.set_state(GameState.PLAYING)
                            game_state.reset_game()
                        else:  # Quit selected
                            running = False
                
                # Game over state
                elif game_state.get_state() == GameState.GAME_OVER:
                    if event.key == pygame.K_SPACE:
                        game_state.set_state(GameState.PLAYING)
                        game_state.reset_game()
                        object_y = 0
                        object_x = random.randint(0, screen_width - object_width)
                    elif event.key == pygame.K_ESCAPE:
                        game_state.set_state(GameState.MENU)
        
        # Get current state
        current_state = game_state.get_state()
        
        # Menu state
        if current_state == GameState.MENU:
            draw_menu(screen, screen_width, screen_height)
            # Update the selection indicator position
            pygame.draw.rect(screen, (255, 0, 0), 
                            (screen_width // 2 - 60, 
                             screen_height // 2 + (50 * menu_selection), 10, 10))
        
        # Playing state
        elif current_state == GameState.PLAYING:
            # Calculate current object speed based on difficulty
            object_speed = game_state.calculate_speed(base_object_speed)
            
            # Update falling object position
            object_y += object_speed

            # Check if object is caught
            bucket_rect = pygame.Rect(posx, posy, bucket_width, bucket_height)
            object_rect = pygame.Rect(object_x, object_y, object_width, object_height)

            if bucket_rect.colliderect(object_rect):
                game_state.score += 1
                play_sound(catch_sound)
                
                # Every 5 points, increase difficulty
                if game_state.score % 5 == 0:
                    game_state.increase_difficulty()
                
                # Reset object
                object_x = random.randint(0, screen_width - object_width)
                object_y = 0
            elif object_y > screen_height:
                # Object missed - game over (one life)
                play_sound(miss_sound)
                game_state.set_state(GameState.GAME_OVER)
            
            # Draw game screen
            screen.fill((154, 200, 255))  # Sky blue background
            
            # Draw bucket with outline
            pygame.draw.rect(screen, bucket_color, bucket_rect)
            pygame.draw.rect(screen, bucket_outline_color, bucket_rect, 2)  # 2px outline

            # Draw falling object
            pygame.draw.rect(screen, object_color, object_rect)
            
            # Draw difficulty indicator
            draw_text(screen, f"Level: {game_state.difficulty_level}", 24, screen_width - 70, 10, (0, 0, 0))
            
            # Draw score
            draw_text(screen, f"Score: {game_state.score}", 24, 70, 10, (0, 0, 0))
        
        # Game over state
        elif current_state == GameState.GAME_OVER:
            draw_game_over(screen, screen_width, screen_height, game_state.score)
        
        pygame.display.update()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

def ServerThread():
    """Network server thread handling client connections"""
    global posx, posy, client_connected
    
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
    
    while True:
        try:
            conn, address = server_socket.accept()
            print("Connection from: " + str(address))
            client_connected = True
            
            # Start game when client connects
            if game_state.get_state() == GameState.MENU:
                # Don't auto-start game, let player press SPACE
                pass
                
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    break
                
                print("from connected user: " + str(data))
                
                # Calculate movement speed based on difficulty
                move_speed = 10 * (1 + (game_state.difficulty_level * 0.1))
                
                # Only process movement if in playing state
                if game_state.get_state() == GameState.PLAYING:
                    if data == 'w':
                        posy -= move_speed
                    if data == 's':
                        posy += move_speed
                    if data == 'a':
                        posx -= move_speed
                    if data == 'd':
                        posx += move_speed
                
                # Allow client to start/restart the game
                elif data == 'space':
                    if game_state.get_state() == GameState.MENU:
                        game_state.set_state(GameState.PLAYING)
                        game_state.reset_game()
                    elif game_state.get_state() == GameState.GAME_OVER:
                        game_state.set_state(GameState.PLAYING)
                        game_state.reset_game()
            
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