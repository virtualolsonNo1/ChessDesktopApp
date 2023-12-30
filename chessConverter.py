import chess
from chess import Board
import serial
import copy
from possibleMoves import piecePossibleMoves

initialPosition = [['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
            ]

lastPosition = None


#This one's a thiccy...
def takenPiece(board, prevPosition, firstArr, secondArr, thirdArr):
        #variable declaration
        file = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        currSquare = None
        newSquare = None
        pieceMoved = None
        newI = None
        newJ = None
        castled = False
        castledSide = None
        secondArrTake = True

        #TODO: MAKE WORK FOR TAKING PIECE FIRST RATHER THAN PICKING UP YOUR PIECE FIRST!!!!
        #loop through arrays and position
        enteredOnce = False
        pieceI = None
        pieceJ = None

        #Loop through first array. If multiple of player's pieces are moved or piece was moved that isn't theirs, then castle or first Array took, otherwise secondArrTake = True
        for i in range(8):
                for j in range(8):
                        #if first array is a 0 but the previous position had a piece there, that is the piece that was moved
                        if firstArr[i][j] == 0 and prevPosition[i][j] != 0:
                                if(enteredOnce):
                                        secondArrTake = False
                                        prevPosition[pieceI][pieceJ] = pieceMoved
                                        break
                                #if it's a piece of the player who's turn it is that was picked up, store said info accordingly
                                if board.turn == chess.WHITE and prevPosition[i][j].isupper() or board.turn == chess.BLACK and prevPosition[i][j].islower():
                                        pieceMoved = prevPosition[i][j]
                                        currSquare = file[j] + str(8 - i)
                                        prevPosition[i][j] = 0
                                        pieceI = i
                                        pieceJ = j

                                        #mark enteredOnce as true if first time entering
                                        enteredOnce = True

                                else:
                                        #if it's the opposing player's piece, we know that secondArrTake = false!!!!! therefore different format of arrays than expected
                                        secondArrTake = False
                                        #TODO: I think this code is redundant and useless!!!!!!
                                        if pieceI is not None and pieceJ is not None:
                                                prevPosition[pieceI][pieceJ] = pieceMoved
                                        break
        #if it follows expected format of first array is your piece, next array is taking, then final array, use this code:
        if secondArrTake:
                for i in range(8):
                        for j in range(8):
                                #if the second array is 0 but the others aren't, that's the piece that was taken
                                if secondArr[i][j] == 0 and firstArr[i][j] != 0 and thirdArr[i][j] != 0:
                                        newSquare = file[j] + str(8 - i)
                                        newI = i
                                        newJ = j
                                #if second array has 0 but previous position doesn't
                                if secondArr[i][j] == 0 and prevPosition[i][j] != 0 and thirdArr[i][j] == 0:
                                        if prevPosition[i][j] == 'P' or prevPosition[i][j] == 'p':
                                                #calculate new home for pawn that took en pessant
                                                if prevPosition[i][j] == 'p':
                                                        newSquare = file[j] + str(8 - i + 1)
                                                        newI = i - 1
                                                        newJ = j
                                                else:
                                                        newSquare = file[j] + str(8 - i - 1)
                                                        newI = i + 1
                                                        newJ = j
                                                prevPosition[i][j] = 0
                                        else:
                                                castledSide = file[j] + str(8 - i)
                                                prevPosition[i][j] = 0
                                                castled = True

        #if piece taken was picked up first or castled by picking up rook first:
        else:
                for i in range(8):
                        for j in range(8):
                                #if second array is a 0 but the previous position had a piece there, that is the piece that was moved
                                if secondArr[i][j] == 0 and prevPosition[i][j] != 0:
                                        #if it's a piece of the player who's turn it is that was picked up, store said info accordingly
                                        if board.turn == chess.WHITE and prevPosition[i][j].isupper() or board.turn == chess.BLACK and prevPosition[i][j].islower():
                                                pieceMoved = prevPosition[i][j]
                                                currSquare = file[j] + str(8 - i)
                                                prevPosition[i][j] = 0

                                #TODO: DO i need the secondArr[i][j] == 0????????
                                #if the first array is 0 but the others aren't, that's the piece that was taken
                                if firstArr[i][j] == 0 and secondArr[i][j] == 0 and thirdArr[i][j] != 0:
                                        newSquare = file[j] + str(8 - i)
                                        newI = i
                                        newJ = j
                                #if first array has 0 but previous position doesn't
                                if firstArr[i][j] == 0 and prevPosition[i][j] != 0 and thirdArr[i][j] == 0:
                                        if prevPosition[i][j] == 'P' or prevPosition[i][j] == 'p':
                                                #calculate new home for pawn that took en pessant
                                                if prevPosition[i][j] == 'p':
                                                        newSquare = file[j] + str(8 - i + 1)
                                                        newI = i - 1
                                                        newJ = j
                                                else:
                                                        newSquare = file[j] + str(8 - i - 1)
                                                        newI = i + 1
                                                        newJ = j
                                                prevPosition[i][j] = 0
                                        else:
                                                castledSide = file[j] + str(8 - i)
                                                prevPosition[i][j] = 0
                                                castled = True


        #update position with moved piece in its new spot
        if newI is not None and newJ is not None: 
                prevPosition[newI][newJ] = pieceMoved
                if (pieceMoved == 'P' or pieceMoved == 'p') and (newI == 0 or newI == 7):
                        newSquare += 'q'
        elif castled:
                #white short castled
                if currSquare == 'h1' or castledSide == 'h1':
                        currSquare = 'e1'
                        newSquare = 'g1'
                        prevPosition[7][6] = 'K'
                        prevPosition[7][5] = 'R'
                #white long castled
                elif currSquare == 'a1' or castledSide == 'a1':
                        currSquare = 'e1'
                        newSquare = 'c1'
                        prevPosition[7][2] = 'K'
                        prevPosition[7][3] = 'R'
                #black short castled
                elif currSquare == 'h8' or castledSide == 'h8':
                        currSquare = 'e8'
                        newSquare = 'g8'
                        prevPosition[0][6] = 'k'
                        prevPosition[0][5] = 'r'
                #black long castled
                elif currSquare == 'a8' or castledSide == 'a8':
                        currSquare = 'e8'
                        newSquare = 'c8'
                        prevPosition[0][2] = 'k'
                        prevPosition[0][3] = 'r'                      
                
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
                if (pieceMoved == 'P' or pieceMoved == 'p') and (newI == 0 or newI == 7):
                        newSquare += 'q'

        return currSquare, newSquare




def main():
        global initialPosition
        # #TODO: ADD ERROR HANDLING WITH LAST POSITION LATER!!!!!
        # global lastPosition 
        # isConn = False
        # while not isConn:
        #         try:
        #                 ser = serial.Serial('COM7')
        #                 print(ser.name)
        #                 isConn = True
        #         except:
        #                 continue

        # #TODO: add shit later to make it work for multiple games, when reset button pressed!!!!!
        # #start a game:
        # board = chess.Board()
        # lastPosition = copy.deepcopy(initialPosition)


        # #TODO: update to better method of receiving data and get sending working eventually for LEDs
        # while True:
        #         line = ser.readline()
        #         strline = line.decode('ascii')
        #         if 'MovePlayed\n' in strline:
        #                 #set lastPosition to initialPosition for error handling purposes
        #                 lastPosition = copy.deepcopy(initialPosition)

        #                 #read in number of arrays that'll be sent
        #                 numArrs = ser.read(1)
        #                 numArrs = int.from_bytes(numArrs, byteorder='big')
        #                 print(numArrs)

        #                 #variable declaration
        #                 arr1 = None
        #                 arr2 = None
        #                 arr3 = None

        #                 #handle if it's a capture/castle vs a movement
        #                 #capture
        #                 if (numArrs == 3):
        #                         arr1 = ser.read(64)
        #                         arr1 = [[arr1[row * 8 + col] for col in range(8)] for row in range(8)]
        #                         arr2 = ser.read(64)
        #                         arr2 = [[arr2[row * 8 + col] for col in range(8)] for row in range(8)]
        #                         arr3 = ser.read(64)
        #                         arr3 = [[arr3[row * 8 + col] for col in range(8)] for row in range(8)]
        #                         currSquare, newSquare = takenPiece(board, initialPosition, arr1, arr2, arr3)
        #                         moveStr = currSquare + newSquare
        #                         board.push_uci(moveStr)
        #                         print(board)
        #                         # correct = "correct"
        #                         # correct = correct.encode('ascii')
        #                         # ser.write(correct)
        #                 #move of piece
        #                 elif (numArrs == 2):
        #                         arr1 = ser.read(64)
        #                         arr1 = [[arr1[row * 8 + col] for col in range(8)] for row in range(8)]
        #                         arr2 = ser.read(64)
        #                         arr2 = [[arr2[row * 8 + col] for col in range(8)] for row in range(8)]
        #                         currSquare, newSquare = pieceMoved(initialPosition, arr1, arr2)
        #                         moveStr = currSquare + newSquare

        #                         #TODO: ADD BETTER RESEND SHIT!!!!!!
        #                         # if moveStr == 'h1h1':
        #                         #         initialPosition = copy.deepcopy(lastPosition)
        #                         #         print("fuck this shit")
        #                         #         resend = "resend\n"
        #                         #         resend = resend.encode('ascii')
        #                         #         ser.write(resend)
        #                         #         continue
        #                         board.push_uci(moveStr)
        #                         print(board)
        #                         # correct = "correct"
        #                         # correct = correct.encode('ascii')
        #                         # ser.write(correct)
        #                 else:
        #                         raise Exception("NUM ARRS SHOULD BE 2 or 3!!!!!")  

        





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

        arr10 = [[1, 0, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 0, 1, 1, 1],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 0, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 0, 1],
                ]
        arr9 = [[1, 0, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 0, 1, 1, 1],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 0, 0],
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

        arr13 = [[1, 0, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 0, 1, 1, 1],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 0, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 0, 1],
                ]

        arr12 = [[1, 0, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 0, 1, 1, 1],
                [0, 0, 1, 0, 0, 0, 0, 0],
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
        
        arr15 = [[1, 0, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 0, 1, 1, 1],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 0, 1, 1, 1],
                [1, 1, 1, 1, 1, 0, 0, 1],
                ]

        arr16 = [[1, 0, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 0, 1, 1, 1],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 0, 0, 1],
                ]
        
        arr17 = [[1, 0, 1, 1, 1, 0, 1, 1],
                [1, 1, 1, 1, 0, 1, 1, 1],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 0, 0, 1],
                ]

        arr18 = [[1, 0, 1, 1, 1, 0, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 0, 0, 1],
                ]
        
        arr19 = [[1, 0, 1, 1, 1, 0, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 0, 0, 0, 1],
                ]
        
        arr20 = [[1, 0, 1, 1, 1, 0, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 0, 0, 0, 0],
                ]
        
        arr21 = [[1, 0, 1, 1, 1, 0, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 0, 1, 1, 0],
                ]
        
        arr22 = [[1, 0, 1, 1, 1, 0, 0, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 0, 1, 1, 0],
                ]
        
        arr23 = [[1, 0, 1, 1, 1, 0, 0, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 0, 1, 1, 0],
                ]
        
        arr22 = [[1, 0, 1, 1, 1, 0, 0, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 0, 1, 1, 0],
                ]
        
        arr23 = [[1, 0, 1, 1, 1, 0, 0, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 0, 1, 1, 0],
                ]
        
        arr24 = [[1, 0, 1, 1, 1, 0, 0, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]
        
        arr25 = [[1, 0, 1, 1, 1, 0, 0, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]
        
        arr26 = [[1, 0, 1, 1, 1, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]
        
        arr27 = [[1, 0, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]
        
        arr28 = [[1, 0, 1, 1, 0, 1, 1, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]
        
        arr29 = [[1, 0, 1, 1, 0, 1, 1, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]
        
        arr30 = [[1, 0, 1, 1, 0, 1, 1, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 1, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]
        
        arr31 = [[1, 0, 1, 1, 0, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 1, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]
        
        arr32 = [[1, 0, 1, 1, 0, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 1, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]
        
        arr33 = [[1, 0, 1, 1, 0, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]
        
        arr34 = [[1, 0, 1, 1, 0, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 0, 0, 1, 0, 0],
                [0, 1, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]
        
        arr35 = [[1, 0, 1, 1, 0, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [1, 0, 0, 0, 0, 1, 0, 0],
                [0, 1, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]
        
        arr36 = [[1, 0, 1, 1, 0, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [1, 0, 0, 0, 0, 1, 0, 1],
                [0, 1, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]

        arr37 = [[1, 0, 1, 1, 0, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [0, 0, 0, 0, 0, 1, 0, 1],
                [0, 1, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]
        
        arr38 = [[1, 0, 1, 1, 0, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [0, 0, 0, 0, 0, 1, 0, 1],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]
        
        arr39 = [[1, 0, 1, 1, 0, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [1, 0, 0, 0, 0, 1, 0, 1],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]
        
        arr40 = [[1, 0, 1, 1, 0, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 0, 0],
                [1, 0, 0, 0, 0, 1, 0, 1],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]
        
        arr41 = [[1, 0, 1, 1, 0, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 0, 0],
                [1, 0, 0, 0, 0, 1, 1, 1],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]

        arr42 = [[1, 0, 1, 1, 0, 1, 1, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [1, 0, 0, 0, 0, 1, 1, 1],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]
        
        arr43 = [[1, 0, 1, 1, 0, 1, 1, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 1, 1, 1],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]
        
        arr44 = [[1, 0, 1, 1, 0, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 1, 1, 1],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]
        
        arr45 = [[1, 0, 1, 1, 0, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 1, 1, 1],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]
        
        arr46 = [[1, 0, 1, 1, 0, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 1],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]
        
        arr47 = [[1, 0, 1, 1, 0, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 1],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]
        
        arr48 = [[0, 0, 1, 1, 0, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 1],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]
        
        arr49 = [[0, 0, 1, 1, 0, 1, 1, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 1],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]
        
        arr50 = [[1, 0, 1, 1, 0, 1, 1, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 1],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0],
                ]


        #start a game:
        board = chess.Board()

        currSquare, newSquare = pieceMoved(initialPosition, arr1, arr2)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)
        print('\n')

        # print(currSquare)
        # print(newSquare)
        # printPos(initialPosition)

        currSquare, newSquare = pieceMoved(initialPosition, arr3, arr4)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)
        print('\n')

        currSquare, newSquare = pieceMoved(initialPosition, arr5, arr6)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)
        print('\n')

        currSquare, newSquare = pieceMoved(initialPosition, arr7, arr8)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)
        print('\n')

        currSquare, newSquare = takenPiece(board, initialPosition, arr9, arr10, arr11)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)
        print('\n')

        currSquare, newSquare = takenPiece(board, initialPosition, arr12, arr13, arr14)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)
        print('\n')

        currSquare, newSquare = pieceMoved(initialPosition, arr15, arr16)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)
        print('\n')

        currSquare, newSquare = pieceMoved(initialPosition, arr17, arr18)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)
        print('\n')

        piecePossibleMoves(board, 7, 4)

        currSquare, newSquare = takenPiece(board, initialPosition, arr19, arr20, arr21)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)
        print('\n')

        currSquare, newSquare = pieceMoved(initialPosition, arr22, arr23)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)
        print('\n')

        currSquare, newSquare = pieceMoved(initialPosition, arr24, arr25)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)
        print('\n')

        currSquare, newSquare = takenPiece(board, initialPosition, arr26, arr27, arr28)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)
        print('\n')

        currSquare, newSquare = pieceMoved(initialPosition, arr29, arr30)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)
        print('\n')

        currSquare, newSquare = pieceMoved(initialPosition, arr31, arr32)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)
        print('\n')

        currSquare, newSquare = pieceMoved(initialPosition, arr33, arr34)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)
        print('\n')

        currSquare, newSquare = pieceMoved(initialPosition, arr35, arr36)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)
        print('\n')

        currSquare, newSquare = takenPiece(board, initialPosition, arr37, arr38, arr39)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)
        print('\n')

        currSquare, newSquare = pieceMoved(initialPosition, arr40, arr41)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)
        print('\n')
        piecePossibleMoves(board, 6, 4)

        currSquare, newSquare = takenPiece(board, initialPosition, arr42, arr43, arr44)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)
        print('\n')

        currSquare, newSquare = takenPiece(board, initialPosition, arr45, arr46, arr47)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)
        print('\n')

        currSquare, newSquare = takenPiece(board, initialPosition, arr48, arr49, arr50)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)
        print('\n')


        print("Second game\n")

        board2 = chess.Board()
        newInitialPosition = [['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
            ]
        arr1 = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 1, 1, 1, 1],
                ]
        
        arr2 = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 1, 1, 1, 1],
                ]
        
        arr3 = [[1, 0, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 1, 1, 1, 1],
                ]
        
        arr4 = [[1, 0, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 1, 1, 1, 1],
                ]
        
        arr5 = [[1, 0, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 1, 1, 1, 1],
                ]
        
        arr6 = [[1, 0, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 1, 1, 1, 1],
                ]
        
        arr7 = [[1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 1, 1, 1, 1],
                ]
        
        arr8 = [[1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [0, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 1, 1, 1, 1],
                ]
        
        arr9 = [[1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [0, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 1, 1, 1, 1, 1],
                ]
        
        arr10 = [[1, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [0, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 1, 1, 1, 1, 1],
                ]
        
        arr11 = [[1, 0, 0, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 1, 1, 1, 1],
                [0, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 1, 1, 1, 1, 1],
                ]
        
        arr12 = [[1, 0, 0, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 1, 1, 1, 1, 1],
                ]
        
        arr13 = [[1, 0, 0, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 0, 0, 0, 0, 0],
                [1, 1, 1, 0, 1, 1, 1, 1],
                [1, 0, 0, 1, 1, 1, 1, 1],
                ]
        
        arr14 = [[1, 0, 0, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 0, 1, 1, 1, 1],
                [1, 0, 0, 1, 1, 1, 1, 1],
                ]
        
        arr15 = [[1, 0, 0, 1, 1, 1, 1, 1],
                [1, 1, 1, 0, 1, 1, 1, 1],
                [0, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 0, 1, 1, 1, 1],
                [1, 0, 0, 1, 1, 1, 1, 1],
                ]
        
        arr16 = [[1, 0, 0, 1, 1, 1, 1, 1],
                [1, 1, 1, 0, 1, 1, 1, 1],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 0, 1, 1, 1, 1],
                [1, 0, 0, 1, 1, 1, 1, 1],
                ]
        
        arr17 = [[1, 0, 0, 1, 1, 1, 1, 1],
                [1, 1, 1, 0, 1, 1, 1, 1],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 0, 1, 1, 1, 1],
                [1, 0, 0, 0, 1, 1, 1, 1],
                ]
        
        arr18 = [[1, 0, 0, 1, 1, 1, 1, 1],
                [1, 1, 1, 0, 1, 1, 1, 1],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 0, 1, 1, 1, 1],
                ]
        
        arr19 = [[1, 0, 0, 0, 1, 1, 1, 1],
                [1, 1, 1, 0, 1, 1, 1, 1],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 0, 1, 1, 1, 1],
                ]
        
        arr20 = [[1, 0, 0, 0, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 0, 1, 1, 1, 1],
                ]
        
        arr22 = [[1, 0, 0, 0, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 1, 1, 1, 1],
                ]
        
        arr21 = [[1, 0, 0, 0, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 1, 1, 1],
                ]
        
        arr23 = [[1, 0, 0, 0, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr24 = [[1, 0, 0, 0, 0, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr25 = [[0, 0, 0, 0, 0, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr26 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr27 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr28 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr29 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr30 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr31 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr32 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 1, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr33 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [0, 1, 1, 1, 1, 1, 1, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 1, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr34 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [0, 1, 1, 1, 1, 1, 1, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [1, 1, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr36 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [0, 1, 1, 1, 1, 1, 1, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [1, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr35 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [0, 1, 1, 1, 1, 1, 1, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr37 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [0, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr38 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [0, 1, 1, 1, 1, 1, 0, 1],
                [1, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr39 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [0, 1, 1, 1, 1, 1, 0, 1],
                [1, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr40 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [0, 1, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr41 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr42 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr43 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 0],
                [0, 0, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr44 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 0],
                [0, 0, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 0, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr45 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 1, 0],
                [0, 0, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 0, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr47 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 0, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr46 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 0, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr48 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 1, 0, 0],
                [1, 1, 1, 1, 1, 0, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr49 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [0, 1, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 1, 0, 0],
                [1, 1, 1, 1, 1, 0, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr50 = [[1, 0, 1, 1, 0, 1, 1, 1],
                [0, 1, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 1, 0, 0],
                [1, 1, 1, 1, 1, 0, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr51 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [0, 1, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 1, 0, 0],
                [1, 1, 1, 1, 1, 0, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr52 = [[0, 0, 1, 1, 0, 1, 1, 1],
                [0, 0, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 1, 0, 0],
                [1, 1, 1, 1, 1, 0, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr53 = [[1, 0, 1, 1, 0, 1, 1, 1],
                [0, 0, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 1, 0, 0],
                [1, 1, 1, 1, 1, 0, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr54 = [[1, 0, 1, 1, 0, 1, 1, 1],
                [0, 0, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 1, 0, 0],
                [0, 1, 1, 1, 1, 0, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr55 = [[1, 0, 1, 1, 0, 1, 1, 1],
                [0, 0, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 0, 1, 0, 0],
                [0, 1, 1, 1, 1, 0, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr56 = [[1, 0, 1, 1, 0, 1, 1, 1],
                [0, 0, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 0, 1, 0, 0],
                [0, 1, 1, 1, 1, 0, 0, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr57 = [[1, 0, 1, 1, 0, 1, 1, 1],
                [0, 0, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 0, 0, 0, 0],
                [0, 1, 1, 1, 1, 0, 0, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr58 = [[1, 0, 1, 1, 0, 1, 1, 1],
                [0, 0, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 1, 1, 0, 0, 0, 0],
                [0, 1, 1, 1, 1, 0, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr59 = [[1, 0, 1, 1, 0, 1, 1, 1],
                [0, 0, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 1, 0, 0, 0, 0],
                [0, 1, 1, 1, 1, 0, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr60 = [[1, 0, 1, 1, 0, 1, 1, 1],
                [0, 0, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 1, 0, 0, 0, 0],
                [0, 1, 1, 1, 1, 0, 1, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr61 = [[1, 0, 1, 1, 0, 1, 1, 1],
                [0, 0, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 1, 0, 0, 0, 0],
                [0, 1, 1, 1, 1, 0, 0, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        
        arr62 = [[1, 0, 1, 1, 0, 1, 1, 1],
                [0, 0, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 1, 0, 0, 0, 0],
                [0, 1, 1, 1, 1, 0, 0, 1],
                [0, 0, 1, 1, 0, 1, 1, 0],
                ]
        
        arr63 = [[1, 0, 1, 1, 0, 1, 1, 1],
                [0, 0, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 1, 0, 0, 0, 0],
                [0, 1, 1, 1, 1, 0, 0, 1],
                [0, 0, 1, 1, 0, 1, 1, 1],
                ]
        

        
        currSquare, newSquare = pieceMoved(newInitialPosition, arr1, arr2)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = pieceMoved(newInitialPosition, arr3, arr4)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = pieceMoved(newInitialPosition, arr5, arr6)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = pieceMoved(newInitialPosition, arr7, arr8)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = pieceMoved(newInitialPosition, arr9, arr10)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = pieceMoved(newInitialPosition, arr11, arr12)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = pieceMoved(newInitialPosition, arr13, arr14)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = pieceMoved(newInitialPosition, arr15, arr16)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = pieceMoved(newInitialPosition, arr17, arr18)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = pieceMoved(newInitialPosition, arr19, arr20)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = takenPiece(board2, newInitialPosition, arr21, arr22, arr23)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = takenPiece(board2, newInitialPosition, arr24, arr25, arr26)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = pieceMoved(newInitialPosition, arr27, arr28)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = pieceMoved(newInitialPosition, arr29, arr30)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = pieceMoved(newInitialPosition, arr31, arr32)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = pieceMoved(newInitialPosition, arr33, arr34)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = takenPiece(board2, newInitialPosition, arr35, arr36, arr37)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = pieceMoved(newInitialPosition, arr38, arr39)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = pieceMoved(newInitialPosition, arr40, arr41)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = pieceMoved(newInitialPosition, arr42, arr43)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = pieceMoved(newInitialPosition, arr44, arr45)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = takenPiece(board2, newInitialPosition, arr46, arr47, arr48)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')
        
        currSquare, newSquare = pieceMoved(newInitialPosition, arr49, arr50)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')
        
        currSquare, newSquare = takenPiece(board2, newInitialPosition, arr51, arr52, arr53)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = pieceMoved(newInitialPosition, arr54, arr55)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = takenPiece(board2, newInitialPosition, arr56, arr57, arr58)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = pieceMoved(newInitialPosition, arr59, arr60)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = takenPiece(board2, newInitialPosition, arr61, arr62, arr63)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')


if __name__ == '__main__':
        main()