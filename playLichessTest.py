import berserk
import time
from berserk.exceptions import ResponseError
import chess

class LichessGamePlayer:
    def __init__(self, api_token):
        # created lichess API session
        self.session = berserk.Client(berserk.TokenSession(api_token))
        self.board = chess.Board()
        self.color = 'white'
        
    def find_ongoing_game(self):
        try:
            # Get ongoing games
            ongoing_games = list(self.session.games.get_ongoing())
            if not ongoing_games:
                print("No ongoing games found!")
                return None
                
            # Get the most recent game
            game = ongoing_games[0]
            game_id = game['gameId']
            print(f"Found ongoing game: {game_id}")
            return game_id
            
        except ResponseError as e:
            print(f"Error finding ongoing game: {e}")
            return None
        
    def connect_to_game(self, game_id):
        try:
            # Get game info
            game = self.session.games.export(game_id)

            # if white username/id matches mine, I'm white, otherwise, I'm black
            self.color = 'white' if game['players']['white']['user']['id'] == self.session.account.get()['id'] else 'black'
            
            # Set up board with any existing moves
            self.board.reset()
            if 'moves' in game:
                # loop through, adding moves to those played
                for move in game['moves'].split():
                    try:
                        self.board.push_san(move)
                    except:
                        pass
            
            print(f"Connected to game {game_id}")
            print(f"Playing as {self.color}")
            print(f"Current position:")
            print(self.board)
            return True
            
        except ResponseError as e:
            print(f"Error connecting to game: {e}")
            return False
            
    def make_move(self, move, game_id):
        """Make a move in Smith notation (e.g., 'a2a4')."""
        try:
            # Validate move format
            if not (len(move) == 4 and 
                    move[0] in 'abcdefgh' and 
                    move[1] in '12345678' and 
                    move[2] in 'abcdefgh' and 
                    move[3] in '12345678'):
                print("Invalid move format! Use Smith notation (e.g., 'a2a4')")
                return False
            
            # Make the move
            self.session.board.make_move(game_id, move)
            
            # Update local board
            try:
                self.board.push_uci(move)
            except:
                pass
                
            print("\nCurrent position:")
            print(self.board)
            return True
            
        except ResponseError as e:
            print(f"Invalid move or error: {e}")
            return False
            
    def get_game_state(self, game_id):
        """Get current game state."""
        try:
            game = self.session.games.export(game_id)
            return {
                'moves': game.get('moves', '').split(),
                'status': game.get('status'),
                'winner': game.get('winner'),
                'white': game.get('white', {}).get('name'),
                'black': game.get('black', {}).get('name'),
                'is_my_turn': self.is_my_turn(game)
            }
        except ResponseError as e:
            print(f"Error getting game state: {e}")
            return None
            
    def is_my_turn(self, game):
        moves = game.get('moves', '').count(' ') + 1
        return (moves % 2 == 0 and self.color == 'white') or (moves % 2 == 1 and self.color == 'black')

    def stream_game(self, game_id):
        try:
            for event in self.session.board.stream_game_state(game_id):
                if 'type' in event and event['type'] == 'gameState':
                    # Update local board
                    self.board.reset()
                    if 'moves' in event:
                        for move in event['moves'].split():
                            try:
                                self.board.push_uci(move)
                            except:
                                pass
                    print("\nUpdated position:")
                    print(self.board)
                    return True
        except ResponseError as e:
            print(f"Error streaming game: {e}")
            return False

def print_instructions():
    """Print move format instructions."""
    print("\nMove Format Instructions:")
    print("Use Smith notation: specify the starting and ending squares")
    print("Format: [start square][end square]")
    print("Examples:")
    print("- a2a4 (moves pawn from a2 to a4)")
    print("- b1c3 (moves knight from b1 to c3)")
    print("- e7e8q (promotes pawn to queen)")
    print("\nCommands:")
    print("- 'status' to see game state")
    print("- 'board' to see current position")
    print("- 'help' to see these instructions")
    print("- 'quit' to exit")

def main():
    # Replace with your Lichess API token
    api_token = "lip_z1BCO08OerMAvpfZda8M"
    player = LichessGamePlayer(api_token)
    
    # Find and connect to most recent ongoing game
    game_id = player.find_ongoing_game()
    if not game_id:
        print("No ongoing games found. Start a game on Lichess first!")
        return
        
    if not player.connect_to_game(game_id):
        print("Failed to connect to game")
        return
        
    print_instructions()
    
    while True:
        # Get current game state
        state = player.get_game_state(game_id)
        if not state:
            print("Error getting game state")
            break
            
        if state['status'] != 'started':
            print(f"Game is over. Status: {state['status']}")
            if state['winner']:
                print(f"Winner: {state['winner']}")
            break
            
        # Wait for our turn
        if ((not state['is_my_turn']) and (len(state['moves']) != 0)):
            print("Waiting for opponent's move...")
            player.stream_game(game_id)
            continue
            
        command = input("\nEnter move: ").strip().lower()
        
        if command == 'quit':
            break
        elif command == 'help':
            print_instructions()
            continue
        elif command == 'board':
            print("\nCurrent position:")
            print(player.board)
            continue
        elif command == 'status':
            print(f"\nMoves: {' '.join(state['moves'])}")
            print(f"Status: {state['status']}")
            continue
            
        if not player.make_move(command, game_id):
            print("Invalid move or error occurred")

if __name__ == "__main__":
    main()