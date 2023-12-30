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

def piecePossibleMoves(piece, pieceI, pieceJ, prevPosition):
    isWhite = None
    if piece.isupper():
        isWhite = True
    else:
        isWhite = False
    numPoss = 0

    #TODO: USE find_move() function!!!!!!!!!!!!!!!
    possMoves = []
    if piece == 'P':
        if(prevPosition[pieceI + 1][pieceJ + 1] != 0 and prevPosition[pieceI + 1][pieceJ + 1].issuper() != isWhite and pieceI + 1 <= 7 and pieceJ <= 7):
            ledState[pieceI + 1][pieceJ + 1] = 1
        if(prevPosition[pieceI + 1][pieceJ - 1] != 0 and prevPosition[pieceI + 1][pieceJ - 1].issuper() != isWhite and pieceI + 1 <= 7 and pieceJ >= 0):
            ledState[pieceI + 1][pieceJ - 1] = 1
        if(prevPosition[pieceI + 1][pieceJ] == 0 and pieceI + 1 <= 7):
            ledState[pieceI + 1][pieceJ] = 1
    elif piece == 'p':
        if(prevPosition[pieceI - 1][pieceJ + 1] != 0 and prevPosition[pieceI - 1][pieceJ + 1].issuper() != isWhite and pieceI - 1 >= 0 and pieceJ + 1 <= 7):
            ledState[pieceI - 1][pieceJ + 1] = 1
        if(prevPosition[pieceI - 1][pieceJ - 1] != 0 and prevPosition[pieceI - 1][pieceJ - 1].issuper() != isWhite and pieceI - 1 >= 0 and pieceJ - 1 >= 0):
            ledState[pieceI - 1][pieceJ - 1] = 1
        if(prevPosition[pieceI - 1][pieceJ] == 0 and pieceI >= 0):
            ledState[pieceI - 1][pieceJ] = 1
    elif piece == 'N' or piece == 'n':
        if(prevPosition[pieceI + 2][pieceJ + 1] != 0 and prevPosition[pieceI + 2][pieceJ + 1].issuper() != isWhite and pieceI + 2 <= 7 and pieceJ + 1 <= 7):
            ledState[pieceI + 2][pieceJ + 1] = 1
        if(prevPosition[pieceI + 2][pieceJ - 1] != 0 and prevPosition[pieceI + 2][pieceJ - 1].issuper() != isWhite and pieceI + 2 <= 7 and pieceJ - 1 >= 0):
            ledState[pieceI + 2][pieceJ - 1] = 1
        if(prevPosition[pieceI - 2][pieceJ + 1] != 0 and prevPosition[pieceI - 2][pieceJ + 1].issuper() != isWhite and pieceI - 2 >= 0 and pieceJ + 1 <= 7):
            ledState[pieceI - 2][pieceJ + 1] = 1
        if(prevPosition[pieceI - 2][pieceJ - 1] != 0 and prevPosition[pieceI - 2][pieceJ - 1].issuper() != isWhite and pieceI - 2 >= 0 and pieceJ - 1 >= 0):
            ledState[pieceI - 2][pieceJ - 1] = 1
        if(prevPosition[pieceI + 1][pieceJ + 2] != 0 and prevPosition[pieceI + 1][pieceJ + 2].issuper() != isWhite and pieceI + 1 <= 7 and pieceJ + 2 <= 7):
            ledState[pieceI + 1][pieceJ + 2] = 1
        if(prevPosition[pieceI + 1][pieceJ - 2] != 0 and prevPosition[pieceI + 1][pieceJ - 2].issuper() != isWhite and pieceI + 1 <= 7 and pieceJ - 2 >= 0):
            ledState[pieceI + 1][pieceJ - 2] = 1
        if(prevPosition[pieceI - 1][pieceJ + 2] != 0 and prevPosition[pieceI - 1][pieceJ + 2].issuper() != isWhite and pieceI - 1 >= 0 and pieceJ + 2 <= 7):
            ledState[pieceI - 1][pieceJ + 2] = 1
        if(prevPosition[pieceI - 1][pieceJ - 2] != 0 and prevPosition[pieceI - 1][pieceJ - 2].issuper() != isWhite and pieceI - 1 >= 0 and pieceJ - 2 >= 0):
            ledState[pieceI - 1][pieceJ - 2] = 1
    elif piece == 'B' or piece == 'b':
        #TODO: NEED TO LOOP THROUGH ARRAY BACKWARDS TO GET OTHER MOVES PROPERLY

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
        ledState[pieceI][pieceJ] = 1
        printPos(prevPosition)
        print('\n')
        printPos(ledState)
        
        

    elif piece == 'R' or piece == 'r':
        return 0
    elif piece == 'Q' or piece == 'q':
        return 0
    elif piece == 'K' or piece == 'k':
        return 0
            


if __name__ == '__main__':

    prevPosition = [
        [0, 0, 'k', 'r', 0, 'b', 'n', 'r'],
        ['P', 'b', 'p', 'q', 'p', 'p', 0, 'p'],
        [0, 'p', 0, 'p', 0, 0, 0, 0],
        [0, 0, 0, 0, 'n', 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 'N', 'P', 0, 'p', 0, 0],
        ['P', 'B', 'P', 'Q', 'P', 0, 'P', 'P'],
        [0, 0, 0, 'R', 'K', 'B', 'N', 'R']
        ]

    piecePossibleMoves('b', 1, 1, prevPosition)


