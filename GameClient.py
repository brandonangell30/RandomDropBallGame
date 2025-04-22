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
        # Special handling for space key (restart game)
        if key == keyboard.Key.space:
            print("Sending SPACE command")
            client_socket.send('space'.encode())
            time.sleep(0.1)  # Small delay to prevent rapid repeat
            return
            
        # Handle WASD movement keys
        if hasattr(key, 'char'):
            if key.char in ['w', 'a', 's', 'd']:
                client_socket.send(key.char.encode())
                time.sleep(0.05)  # Small delay to prevent flooding
            
    except Exception as e:
        print(f"Error sending command: {e}")
        connected = False

def on_release(key):
    """Handle key release events"""
    global client_socket, connected
    
    # Handle quit keys (ESC or Q)
    if key == keyboard.Key.esc:
        print("ESC pressed - Disconnecting from server...")
        if client_socket and connected:
            try:
                client_socket.close()
            except:
                pass
        return False  # Stop listener
        
    if hasattr(key, 'char') and key.char == 'q':
        print("Q pressed - Disconnecting from server...")
        if client_socket and connected:
            try:
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