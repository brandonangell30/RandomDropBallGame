# game_state.py
class GameState:
    """
    Class to manage different game states
    """
    # Game state constants
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    
    def __init__(self):
        self.current_state = self.MENU
        self.score = 0
        self.difficulty_level = 1
        
    def reset_game(self):
        """Reset game parameters for a new game"""
        self.score = 0
        self.difficulty_level = 1
        
    def increase_difficulty(self):
        """Increase the difficulty level"""
        self.difficulty_level += 1
        
    def calculate_speed(self, base_speed):
        """Calculate current speed based on difficulty level"""
        return base_speed + (self.difficulty_level * 0.5)
    
    def set_state(self, state):
        """Set the current game state"""
        self.current_state = state
        
    def get_state(self):
        """Get the current game state"""
        return self.current_state