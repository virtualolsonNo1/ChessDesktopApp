import chess

initialPosition = [['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
            ]

def printPos(position):
    for p in position:
        for piece in p:
            print(str(piece), end=" ")
        print("\n")

def pieceMoved(arr, position):
    for i in range(0, 8):
        for j in range(0, 8):
            if arr[i][j] == 0 and position[i][j] != 0:
                return position[i][j]
            
def arrToPosition(arr, position):
    piece = None
    newI = None
    newJ = None
    for i in range(0, 8):
        for j in range(0, 8):
            if arr[i][j] == 0 and position[i][j] != 0:
                piece = position[i][j]
                position[i][j] = 0
            elif arr[i][j] == 1 and position[i][j] == 0:
                newI = i
                newJ = j
    position[newI][newJ] = piece

def squareUpdateNoTake(prevArr, currArr):
    prevSquare = None
    currSquare = None
    file = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    for i in range(0, 8):
        for j in range(0, 8):
            if prevArr[i][j] != currArr[i][j]:
                if currArr[i][j] == 0:
                    prevSquare = file[j] + str(8 - i)
                else:
                    currSquare = file[j] + str(8 - i)
    return prevSquare, currSquare

def squareUpdateTake(prevArr, currArr):
    return 0, 1


def numDifferences(prevArr, currArr):
    numDiff = 0
    for i in range(0, 8):
        for j in range(0, 8):
            if prevArr[i][j] != currArr[i][j]:
                numDiff += 1
    return numDiff



def piecePotentialTakes(piece, i, j, prevPosition):
    isWhite = None
    if piece.issuper():
        isWhite = True
    else:
        isWhite = False
    numPoss = 0


    #TODO: add en pessant later, but not a rn issue, WAAAAAY more pressing stuff atm
    if piece == 'P':
        #TOOD: will this shit throw error if not within bounds? idk python well enough lol
        if(prevPosition[i - 1][j + 1] != 0 and prevPosition[i - 1][j + 1].issuper() != isWhite):
            numPoss += 1
        if(prevPosition[i - 1][j - 1] != 0 and prevPosition[i - 1][j - 1].issuper() != isWhite):
            numPoss += 1
    elif piece == 'p':
        if(prevPosition[i + 1][j + 1] != 0 and prevPosition[i + 1][j + 1].issuper() != isWhite):
            numPoss += 1
        if(prevPosition[i + 1][j - 1] != 0 and prevPosition[i + 1][j - 1].issuper() != isWhite):
            numPoss += 1
    elif piece == 'N' or piece == 'n':
        if(prevPosition[i + 2][j + 1] != 0 and prevPosition[i + 2][j + 1].issuper() != isWhite):
            numPoss += 1
        if(prevPosition[i + 2][j - 1] != 0 and prevPosition[i + 2][j - 1].issuper() != isWhite):
            numPoss += 1
        if(prevPosition[i - 2][j + 1] != 0 and prevPosition[i - 2][j + 1].issuper() != isWhite):
            numPoss += 1
        if(prevPosition[i - 2][j - 1] != 0 and prevPosition[i - 2][j - 1].issuper() != isWhite):
            numPoss += 1
        if(prevPosition[i + 1][j + 2] != 0 and prevPosition[i + 1][j + 2].issuper() != isWhite):
            numPoss += 1
        if(prevPosition[i + 1][j - 2] != 0 and prevPosition[i + 1][j - 2].issuper() != isWhite):
            numPoss += 1
        if(prevPosition[i - 1][j + 2] != 0 and prevPosition[i - 1][j + 2].issuper() != isWhite):
            numPoss += 1
        if(prevPosition[i - 1][j - 2] != 0 and prevPosition[i - 1][j - 2].issuper() != isWhite):
            numPoss += 1
    elif piece == 'B' or piece == 'b':
        return 0
    elif piece == 'R' or piece == 'r':
        return 0
    elif piece == 'Q' or piece == 'q':
        return 0
    elif piece == 'K' or piece == 'k':
        return 0


def main():
    #TODO: will need to convert from array to 2d array later, as data not stored like this rn on board
    arr1 = [[1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            ]
    
    arr2 = [[1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            ]
    
    arr3 = [[1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            ]
    
    # x = numDifferences(arr1, arr2)
    # if(numDifferences == 2):
    #     prevSquare, currSquare = squareUpdateNoTake(arr1, arr2)
    # else:
    #     prevSquare, currSquare = squareUpdateTake(arr1, arr2)
    # print(f'Previous Square: {prevSquare}\n')
    # print(f'Current Square: {currSquare}\n')

    arrToPosition(arr2, initialPosition)
    printPos(initialPosition)


if __name__ == '__main__':
    main()