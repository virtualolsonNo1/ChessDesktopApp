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

#TODO: Add third function to take care of castling!!!!!

def takenPiece (prevPosition, firstArr, secondArr, thirdArr):
        #TODO: ADD EN PESSANT!!!
        #variable declaration
        file = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        currSquare = None
        newSquare = None
        pieceTaken = None
        pieceMoved = None
        secondPieceMoved = None
        newI = None
        newJ = None
        firstPieceMoved = False
        castled = False
        castledSide = None

        #TODO: MAKE WORK FOR TAKING PIECE FIRST RATHER THAN PICKING UP YOUR PIECE FIRST!!!!
        #loop through arrays and position
        for i in range(8):
                for j in range(8):
                        #if first array is a 0 but the previous position had a piece there, that is the piece that was moved
                        if firstArr[i][j] == 0 and prevPosition[i][j] != 0 and not firstPieceMoved:
                                pieceMoved = prevPosition[i][j]
                                currSquare = file[j] + str(8 - i)
                                prevPosition[i][j] = 0
                        #if the second array is 0 but the others aren't, that's the piece that was taken
                        if secondArr[i][j] == 0 and firstArr[i][j] != 0 and thirdArr[i][j] != 0:
                                newSquare = file[j] + str(8 - i)
                                pieceTaken = prevPosition[i][j]
                                newI = i
                                newJ = j
                        #if second array has 0 but previous position doesn't
                        if secondArr[i][j] == 0 and prevPosition[i][j] != 0 and thirdArr[i][j] == 0:
                                castledSide = file[j] + str(8 - i)
                                prevPosition[i][j] = 0
                                castled = True
        #update position with moved piece in its new spot
        if newI is not None and newJ is not None: 
                prevPosition[newI][newJ] = pieceMoved
        elif castled:
                if currSquare == 'h1' or castledSide == 'h1':
                        currSquare = 'e1'
                        newSquare = 'g1'
                elif currSquare == 'a1' or castledSide == 'a1':
                        currSquare = 'e1'
                        newSquare = 'c1'
                elif currSquare == 'h8' or castledSide == 'h8':
                        currSquare = 'e8'
                        newSquare = 'g8'
                elif currSquare == 'a8' or castledSide == 'a8':
                        currSquare = 'e8'
                        newSquare = 'c8'

                        
                
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

        #TODO: improve connection process so can try to connect until board is ready, not having to start this after board is running
        # ser = serial.Serial('COM7')
        # print(ser.name)

        # #TODO: add shit later to make it work for multiple games
        # #start a game:
        # board = chess.Board()

        # #TODO: update to better method of receiving data and get sending working eventually for LEDs
        # while True:
        #         line = ser.readline()
        #         strline = line.decode('ascii')
        #         if 'MovePlayed\n' in strline:
        #                 extra0 = ser.read(1)
        #                 print(extra0)
        #                 numArrs = ser.read(1)
        #                 numArrs = int.from_bytes(numArrs, byteorder='big')
        #                 print(numArrs)
        #                 arr1 = None
        #                 arr2 = None
        #                 arr3 = None
        #                 if (numArrs == 3):
        #                         arr1 = ser.read(64)
        #                         arr1 = [[arr1[row * 8 + col] for col in range(8)] for row in range(8)]
        #                         arr2 = ser.read(64)
        #                         arr2 = [[arr2[row * 8 + col] for col in range(8)] for row in range(8)]
        #                         arr3 = ser.read(64)
        #                         arr3 = [[arr3[row * 8 + col] for col in range(8)] for row in range(8)]
        #                 elif (numArrs == 2):
        #                         arr1 = ser.read(64)
        #                         arr1 = [[arr1[row * 8 + col] for col in range(8)] for row in range(8)]
        #                         arr2 = ser.read(64)
        #                         arr2 = [[arr2[row * 8 + col] for col in range(8)] for row in range(8)]
        #                 else:
        #                         raise Exception("NUM ARRS SHOULD BE 2 or 3!!!!!")  
        #                 print(arr1)
        #                 print(arr2)

        #                 currSquare, newSquare = pieceMoved(initialPosition, arr1, arr2)
        #                 moveStr = currSquare + newSquare
        #                 board.push_uci(moveStr)
        #                 print(board)

        





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

        currSquare, newSquare = pieceMoved(initialPosition, arr15, arr16)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)

        currSquare, newSquare = pieceMoved(initialPosition, arr17, arr18)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)

        currSquare, newSquare = takenPiece(initialPosition, arr19, arr20, arr21)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)

        currSquare, newSquare = pieceMoved(initialPosition, arr22, arr23)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)

        currSquare, newSquare = pieceMoved(initialPosition, arr24, arr25)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)

        currSquare, newSquare = takenPiece(initialPosition, arr26, arr27, arr28)
        moveStr = currSquare + newSquare
        board.push_uci(moveStr)
        print(board)

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
        
        arr21 = [[1, 0, 0, 0, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 1, 1, 1, 1],
                ]
        
        arr22 = [[1, 0, 0, 0, 1, 1, 1, 1],
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

        currSquare, newSquare = takenPiece(newInitialPosition, arr21, arr22, arr23)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')

        currSquare, newSquare = takenPiece(newInitialPosition, arr24, arr25, arr26)
        moveStr = currSquare + newSquare
        board2.push_uci(moveStr)
        print(board2)
        print('\n')





if __name__ == '__main__':
        main()