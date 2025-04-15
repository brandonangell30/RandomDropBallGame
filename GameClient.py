from pynput import keyboard
import socket
import time
import sys

# Server connection details
server_ip = input("Enter server IP (or press Enter for default): ")
if not server_ip:
    server_ip = "127.0.0.1"  # Default to localhost if no IP provided
    
port = 5000

# Initialize connection status
connected = False
client_socket = None

def connect_to_server():
    """Attempt to connect to the game server"""
    global connected, client_socket
    
    try:
        client_socket = socket.socket()
        client_socket.connect((server_ip, port))
        connected = True
        print(f"Connected to server at {server_ip}:{port}")
        print("Game Controls:")
        print("  W/A/S/D - Move the bucket")
        print("  SPACE - Start/restart game")
        print("  Q or ESC - Quit")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        print("Retrying in 5 seconds...")
        time.sleep(5)
        return False

def on_press(key):
    """Handle key press events"""
    global connected, client_socket
    
    if not connected:
        print("Not connected to server. Attempting to reconnect...")
        connected = connect_to_server()
        return
        
    try:
        # Movement controls
        if hasattr(key, 'char') and key.char in ['w', 'a', 's', 'd']:
            client_socket.send(key.char.encode())
        
        # Special keys
        if key == keyboard.Key.space:
            client_socket.send('space'.encode())
            
    except (AttributeError, socket.error) as e:
        print(f"Error: {e}")
        connected = False

def on_release(key):
    """Handle key release events"""
    if key == keyboard.Key.esc or (hasattr(key, 'char') and key.char == 'q'):
        print("Disconnecting from server...")
        try:
            if client_socket:
                client_socket.close()
        except:
            pass
        return False  # Stop listener

def main():
    """Main function to run the client"""
    global connected
    
    print("Bucket Catch Game - Client")
    print("==========================")
    print(f"Connecting to server at {server_ip}:{port}...")
    
    # Initial connection attempt
    connected = connect_to_server()
    
    if not connected:
        print("Failed to connect. Make sure the server is running.")
        print("Press any key to retry or ESC to quit.")
    
    # Start keyboard listener
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == "__main__":
    main()