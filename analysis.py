import chess
import chess.pgn
import webbrowser

def open_game_in_chesscom(board):
    """
    Opens a chess game in the browser for direct analysis on Chess.com.
    :param board: A chess.Board object
    """
    # Create a game from the board
    game = chess.pgn.Game.from_board(board)
    
    # Extract PGN string directly from the game object
    pgn = str(game)
    
    # Construct the Chess.com analysis URL with the encoded PGN
    analysis_url = f"https://www.chess.com/analysis?pgn={pgn}"
    
    # Open the URL in the default web browser
    webbrowser.open(analysis_url)

# Example usage
def main():
    # Create a new chess board
    board = chess.Board()
    
    # Make some moves
    moves = ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Ba4", "Nf6", "O-O", "Be7"]  # Ruy Lopez
    for move in moves:
        board.push_san(move)
    
    # Open the game in Chess.com
    open_game_in_chesscom(board)

if __name__ == "__main__":
    main()