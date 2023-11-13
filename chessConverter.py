import chess
import serial

initialPosition = [['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
            ]


#Unneeded with python chess library
# #print position for user to view
# def printPos(position):
#     for p in position:
#         for piece in p:
#             print(str(piece), end=" ")
#         print("\n")


def takenPiece(prevPosition, firstArr, secondArr, thirdArr):
    #variable declaration
    file = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    currSquare = None
    newSquare = None
    pieceTaken = None
    pieceMoved = None
    newI = None
    newJ = None

    #loop through arrays and position
    for i in range(8):
        for j in range(8):
            #if first array is a 0 but the previous position had a piece there, that is the piece that was moved
            if firstArr[i][j] == 0 and prevPosition[i][j] != 0:
                pieceMoved = prevPosition[i][j]
                currSquare = file[j] + str(8 - i)
                prevPosition[i][j] = 0
            #if the second array is 0 but the others aren't, that's the piece that was taken
            if secondArr[i][j] == 0 and firstArr[i][j] != 0 and thirdArr[i][j] != 0:
                newSquare = file[j] + str(8 - i)
                pieceTaken = prevPosition[i][j]
                newI = i
                newJ = j
    #update position with moved piece in its new spot
    if newI is not None and newJ is not None:
        prevPosition[newI][newJ] = pieceMoved
    return currSquare, newSquare
            

def pieceMoved(prevPosition, firstArr, secondArr):
    #variable declaration
    file = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    currSquare = None
    newSquare = None
    pieceMoved = None
    newI = None
    newJ = None

    #loop through arrays and position
    for i in range(8):
        for j in range(8):

            #if first array is 0 and previous position isn't, that's the piece that's moved
            if firstArr[i][j] == 0 and prevPosition[i][j] != 0:
                pieceMoved = prevPosition[i][j]
                currSquare = file[j] + str(8 - i)
                prevPosition[i][j] = 0
            #if second array is 1 and first array isn't, then that's the new square
            if secondArr[i][j] == 1 and firstArr[i][j] == 0:
                newSquare = file[j] + str(8 - i)
                newI = i
                newJ = j
    if newI is not None and newJ is not None:
        prevPosition[newI][newJ] = pieceMoved

    return currSquare, newSquare




def main():
    #TODO: will need to convert from array to 2d array later, as data not stored like this rn on board
    #Move Arrs

    ser = serial.Serial('COM7')
    print(ser.name)
    line = ser.readline()
    print(line)





    print(chess.__file__)
    arr1 = [[1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 1, 1, 1],
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
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            ]
    
    arr4 = [[1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            ]
    
    arr5 = [[1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 1],
            ]
    
    arr6 = [[1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 1],
            ]
    
    arr7 = [[1, 0, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 1],
            ]
    
    arr8 = [[1, 0, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 1],
            ]
    
    arr9 = [[1, 0, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 1],
            ]
    arr10 = [[1, 0, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 1],
            ]
    
    arr11 = [[1, 0, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 1],
            ]
    
    arr12 = [[1, 0, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 1],
            ]
    
    arr13 = [[1, 0, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 1],
            ]
    
    arr14 = [[1, 0, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 1],
            ]


    #start a game:
    board = chess.Board()

    currSquare, newSquare = pieceMoved(initialPosition, arr1, arr2)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)

    # print(currSquare)
    # print(newSquare)
    # printPos(initialPosition)

    currSquare, newSquare = pieceMoved(initialPosition, arr3, arr4)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)

    currSquare, newSquare = pieceMoved(initialPosition, arr5, arr6)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)

    currSquare, newSquare = pieceMoved(initialPosition, arr7, arr8)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)

    currSquare, newSquare = takenPiece(initialPosition, arr9, arr10, arr11)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)

    currSquare, newSquare = takenPiece(initialPosition, arr12, arr13, arr14)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)





if __name__ == '__main__':
    main()