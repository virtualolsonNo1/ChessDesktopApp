import chess

def printPos(position):
    for p in position:
        for piece in p:
            print(str(piece), end=" ")
        print("\n")


initialPosition = [['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
            ]

ledState = [[0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
            ]


#TODO: PLAN!!!!!
#   - report when piece picked up, we send back lights for possible moves
#   - rest handled on chess board, where it can turn off all LEDs if piece put back or the led of square it moved onto of allowed squares

def piecePossibleMoves(board, pieceI, pieceJ):
    #TODO: WHAT IF TURNED OFF LED WHEN YOU LAND ON IT TO HELP USER KNOW PIECE THERE!!!!!!!!!
    #TODO: can use has_en_passant and has_kingside/queenside_castling_rights
    #TODO: use find_move with every 1 in array after is_pinned, as you'd think is_pinned and is_check would be good, but if check, can maybe use piece to block..., so this seems easier
    file = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    pieceSquare = file[pieceJ] + str(8 - pieceI)





    legal_moves = list(board.legal_moves)
    valid_moves = [move for move in legal_moves if pieceSquare in chess.square_name(move.from_square)]
    print(valid_moves)
    empty_board = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
        ]
    
    for move in valid_moves:
        empty_board[7 - chess.square_rank(move.to_square)][chess.square_file(move.to_square)] = 1

    printPos(empty_board)
    return empty_board
            


if __name__ == '__main__':

    prevPosBishopTest = [
        [0, 0, 'k', 'r', 0, 'b', 'n', 'r'],
        ['P', 'b', 'p', 'q', 'p', 'p', 0, 'p'],
        [0, 'p', 0, 'p', 0, 0, 0, 0],
        [0, 0, 0, 0, 'n', 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 'N', 'P', 0, 'p', 0, 0],
        ['P', 'B', 'P', 'Q', 'P', 0, 'P', 'P'],
        [0, 0, 0, 'R', 'K', 'B', 'N', 'R']
        ]


