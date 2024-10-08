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


def piecePossibleMoves(board, pieceI, pieceJ):
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
            
def convert_2d_to_1d_bitarray(array_2d):
    result = []
    
    for row in array_2d:
        byte = 0
        # Combine the bits into a single byte
        for i in range(8):
            byte = (byte << 1) | (row[i] & 1)  # Shift left and OR the next bit (ensure only the last bit of the value is used)
        result.append(byte)
    
    return result

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


