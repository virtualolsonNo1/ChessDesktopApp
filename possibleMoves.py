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

def findPosBishop(pieceI, pieceJ, prevPosition, isWhite):
    #down and to right
        for i in range(pieceI + 1, 8):
            #if hits right limit before up, also leave the for loop
            if pieceJ + (i - pieceI) > 7:
                break
            #potential moves diagonally up and to the right
            if prevPosition[i][pieceJ + (i - pieceI)] == 0:
                ledState[i][pieceJ + (i - pieceI)] = 1
            elif prevPosition[i][pieceJ + (i - pieceI)].isupper() != isWhite:
                ledState[i][pieceJ + (i - pieceI)] = 1
                break
            else:
                break

        #down and to the left
        for i in range(pieceI + 1, 8):
            #if hits left limit before up, also leave the for loop
            if pieceJ - (i - pieceI) < 0:
                break
            #potential moves diagonally down and to the right
            if prevPosition[i][pieceJ - (i - pieceI)] == 0:
                ledState[i][pieceJ - (i - pieceI)] = 1
            elif prevPosition[i][pieceJ - (i - pieceI)].isupper() != isWhite:
                ledState[i][pieceJ - (i - pieceI)] = 1
                break
            else:
                break


        #up and to the right
        for i in reversed(range(0, pieceI)):
            #if hits left limit before up, also leave the for loop
            if pieceJ + (pieceI - i) > 7:
                break
            #potential moves diagonally down and to the right
            if prevPosition[i][pieceJ + (pieceI - i)] == 0:
                ledState[i][pieceJ + (pieceI - i)] = 1
            elif prevPosition[i][pieceJ + (pieceI - i)].isupper() != isWhite:
                ledState[i][pieceJ + (pieceI - i)] = 1
                break
            else:
                break

        #up and to the left
        for i in reversed(range(0, pieceI)):
            #if hits left limit before up, also leave the for loop
            if pieceJ - (pieceI - i) < 0:
                break
            #potential moves diagonally down and to the right
            if prevPosition[i][pieceJ - (pieceI - i)] == 0:
                ledState[i][pieceJ - (pieceI - i)] = 1
            elif prevPosition[i][pieceJ - (pieceI - i)].isupper() != isWhite:
                ledState[i][pieceJ - (pieceI - i)] = 1
                break
            else:
                break
        printPos(prevPosition)
        print('\n')
        printPos(ledState)


#TODO: PLAN!!!!!
#   - report when piece picked up, we send back lights for possible moves
#   - rest handled on chess board, where it can turn off all LEDs if piece put back or the led of square it moved onto of allowed squares

def piecePossibleMoves(piece, pieceI, pieceJ, prevPosition):
    #TODO: WHAT IF TURNED OFF LED WHEN YOU LAND ON IT TO HELP USER KNOW PIECE THERE!!!!!!!!!
    #TODO: can use has_en_passant and has_kingside/queenside_castling_rights
    #TODO: use find_move with every 1 in array after is_pinned, as you'd think is_pinned and is_check would be good, but if check, can maybe use piece to block..., so this seems easier
    isWhite = None
    if piece.isupper():
        isWhite = True
    else:
        isWhite = False

    #if the piece is a white pawn
    if piece == 'P':
        #TODO: add || is_en_passant with this square if possible
        #pawn capture to the right
        if(prevPosition[pieceI - 1][pieceJ + 1] != 0 and prevPosition[pieceI - 1][pieceJ + 1].issuper() != isWhite and pieceI - 1 >= 0 and pieceJ + 1 <= 7):
            ledState[pieceI - 1][pieceJ + 1] = 1
        #pawn capture to the left
        if(prevPosition[pieceI - 1][pieceJ - 1] != 0 and prevPosition[pieceI - 1][pieceJ - 1].issuper() != isWhite and pieceI - 1 >= 0 and pieceJ - 1 >= 0):
            ledState[pieceI - 1][pieceJ - 1] = 1
        #pawn move forward
        if(prevPosition[pieceI - 1][pieceJ] == 0 and pieceI >= 0):
            ledState[pieceI - 1][pieceJ] = 1
    #if the piece is a black pawn
    elif piece == 'p':
        #pawn capture to the right
        if(prevPosition[pieceI + 1][pieceJ + 1] != 0 and prevPosition[pieceI + 1][pieceJ + 1].issuper() != isWhite and pieceI + 1 <= 7 and pieceJ <= 7):
            ledState[pieceI + 1][pieceJ + 1] = 1
        #pawn capture to the left
        if(prevPosition[pieceI + 1][pieceJ - 1] != 0 and prevPosition[pieceI + 1][pieceJ - 1].issuper() != isWhite and pieceI + 1 <= 7 and pieceJ >= 0):
            ledState[pieceI + 1][pieceJ - 1] = 1
        #pawn move forward
        if(prevPosition[pieceI + 1][pieceJ] == 0 and pieceI + 1 <= 7):
            ledState[pieceI + 1][pieceJ] = 1
    #if the piece is a knight
    elif piece == 'N' or piece == 'n':
        #2 down and 1 to the right
        if(prevPosition[pieceI + 2][pieceJ + 1] != 0 and prevPosition[pieceI + 2][pieceJ + 1].issuper() != isWhite and pieceI + 2 <= 7 and pieceJ + 1 <= 7):
            ledState[pieceI + 2][pieceJ + 1] = 1
        #2 down and 1 to the left
        if(prevPosition[pieceI + 2][pieceJ - 1] != 0 and prevPosition[pieceI + 2][pieceJ - 1].issuper() != isWhite and pieceI + 2 <= 7 and pieceJ - 1 >= 0):
            ledState[pieceI + 2][pieceJ - 1] = 1
        #2 up and 1 to the right
        if(prevPosition[pieceI - 2][pieceJ + 1] != 0 and prevPosition[pieceI - 2][pieceJ + 1].issuper() != isWhite and pieceI - 2 >= 0 and pieceJ + 1 <= 7):
            ledState[pieceI - 2][pieceJ + 1] = 1
        #2 up and 1 to the left
        if(prevPosition[pieceI - 2][pieceJ - 1] != 0 and prevPosition[pieceI - 2][pieceJ - 1].issuper() != isWhite and pieceI - 2 >= 0 and pieceJ - 1 >= 0):
            ledState[pieceI - 2][pieceJ - 1] = 1
        #1 down and 2 to the right
        if(prevPosition[pieceI + 1][pieceJ + 2] != 0 and prevPosition[pieceI + 1][pieceJ + 2].issuper() != isWhite and pieceI + 1 <= 7 and pieceJ + 2 <= 7):
            ledState[pieceI + 1][pieceJ + 2] = 1
        #1 down and 2 to the left
        if(prevPosition[pieceI + 1][pieceJ - 2] != 0 and prevPosition[pieceI + 1][pieceJ - 2].issuper() != isWhite and pieceI + 1 <= 7 and pieceJ - 2 >= 0):
            ledState[pieceI + 1][pieceJ - 2] = 1
        #1 up and 2 to the right
        if(prevPosition[pieceI - 1][pieceJ + 2] != 0 and prevPosition[pieceI - 1][pieceJ + 2].issuper() != isWhite and pieceI - 1 >= 0 and pieceJ + 2 <= 7):
            ledState[pieceI - 1][pieceJ + 2] = 1
        #1 up and 2 to the left
        if(prevPosition[pieceI - 1][pieceJ - 2] != 0 and prevPosition[pieceI - 1][pieceJ - 2].issuper() != isWhite and pieceI - 1 >= 0 and pieceJ - 2 >= 0):
            ledState[pieceI - 1][pieceJ - 2] = 1

    #If the piece is a bishop
    elif piece == 'B' or piece == 'b':
        findPosBishop(pieceI, pieceJ, prevPosition, isWhite)
        
        
    #if the piece is a rook
    elif piece == 'R' or piece == 'r':
        return 0
    #if the piece is a queen
    elif piece == 'Q' or piece == 'q':
        findPosBishop(pieceI, pieceJ, prevPosition, isWhite)
        #TODO: add rook function as well
        return 0
    #if the piece is a king
    elif piece == 'K' or piece == 'k':
        return 0
            


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

    piecePossibleMoves('b', 1, 1, prevPosBishopTest)


