import chess
from chess import Board
# import serial
import copy
from possibleMoves import piecePossibleMoves
import hid
import time
from hidFuncs import find_device, VENDOR_ID, PRODUCT_ID
import struct

class HIDClockModeReports:
    def __init__(self):
        self.reportId = 0
        self.firstPickupRow = 0
        self.firstPickupCol = 0
        self.secondPickupState = [[0 for _ in range(8)] for _ in range(8)]
        self.secondPickupRow = 0
        self.secondPickupCol = 0
        self.thirdPickupState = [[0 for _ in range(8)] for _ in range(8)]

    @classmethod
    def from_bytes(cls, data):
        report = cls()
        report.reportId, report.firstPickupRow, report.firstPickupCol = struct.unpack('<BBB', data[:3])
        
        if report.reportId == 1:
            # For Report 1, unpack secondPickupState
            for i in range(8):
                report.secondPickupState[i] = list(data[(3+i*8):(3+(i+1)*8)])
        elif report.reportId == 2:
            # For Report 2, unpack secondPickupCol, secondPickupRow, and thirdPickupState
            report.secondPickupRow, report.secondPickupCol = struct.unpack('<BB', data[3:5])
            for i in range(8):
                report.thirdPickupState[i] = list(data[(5+i*8):(5+(i+1)*8)])
        
        return report

    def __str__(self):
        if self.reportId == 1:
            return f"Report 1: firstPickup({self.firstPickupCol}, {self.firstPickupRow}), secondPickupState: {self.secondPickupState}"
        elif self.reportId == 2:
            return f"Report 2: firstPickup({self.firstPickupCol}, {self.firstPickupRow}), secondPickup({self.secondPickupCol}, {self.secondPickupRow}), thirdPickupState: {self.thirdPickupState}"
        else:
            return f"Unknown Report: {self.reportId}"

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

#TODO: PLAN!!!!!
#   - report when piece picked up, we send back lights for possible moves
#   - rest handled on chess board, where it can turn off all LEDs if piece put back down or the led of square it moved onto of allowed squares

#TODO: LATER AFTER ABOVE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#TODO: send squares for the move (should be similar/same for takes and moves) instead of just arrays, and then make your move and call it a day. WAAAAAAY easier than this shit
#TODO: add ability to redo move if they send invalid move
#TODO: add no clock mode where it sends move after opponent piece moves???????


#This one's a thiccy...
def takenPiece(board, prevPosition, firstPickupRow, firstPickupCol, secondPickupRow, secondPickupCol, thirdArr):
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

    #loop through arrays and position
    pieceI = None
    pieceJ = None
    
    #if second piece was the person playing's piece 
    if board.turn == chess.WHITE and prevPosition[secondPickupRow][secondPickupCol].isupper() or board.turn == chess.BLACK and prevPosition[secondPickupRow][secondPickupCol].islower():
        tempI = firstPickupRow
        tempJ = firstPickupCol
        firstPickupRow = secondPickupRow
        firstPickupCol = secondPickupCol
        secondPickupRow = tempI
        secondPickupCol = tempJ
        
    pieceMoved = prevPosition[firstPickupRow][firstPickupCol]

    #if first piece was the person playing's piece, and the second piece isn't, 
    if (board.turn == chess.BLACK and prevPosition[secondPickupRow][secondPickupCol].isupper() or board.turn == chess.WHITE and prevPosition[secondPickupRow][secondPickupCol].islower()):
        prevPosition[firstPickupRow][firstPickupCol] = 0
        pieceI = firstPickupRow
        pieceJ = firstPickupCol
        currSquare = file[firstPickupCol] + str(8 - firstPickupRow)
        newI = secondPickupRow
        newJ = secondPickupCol

        #check for en pessant
        if (thirdArr[secondPickupRow][secondPickupCol] != 1):
            #calculate new home for pawn that took en pessant
            if prevPosition[secondPickupRow][secondPickupCol] == 'p':
                # set new square to 1 rank higher than spot opponent pawn was at
                newSquare = file[secondPickupCol] + str(8 - secondPickupRow + 1)
                newI = secondPickupRow - 1
                newJ = secondPickupCol
            else:
                # set new square to 1 rank lower than spot opponent pawn was at
                newSquare = file[secondPickupCol] + str(8 - secondPickupRow - 1)
                newI = secondPickupRow + 1
                newJ = secondPickupCol
            prevPosition[secondPickupRow][secondPickupCol] = 0
        else:
            newSquare = file[secondPickupCol] + str(8 - secondPickupRow)
        
    # must be castling?????????????????????????
    elif ((prevPosition[firstPickupRow][firstPickupCol].isupper() and prevPosition[secondPickupRow][secondPickupCol].isupper()) or (prevPosition[firstPickupRow][firstPickupCol].islower() and prevPosition[secondPickupRow][secondPickupCol].islower())):
        castledSide = file[secondPickupCol] + str(8 - secondPickupRow)
        currSquare = file[firstPickupCol] + str(8 - firstPickupRow)
        prevPosition[firstPickupRow][firstPickupCol] = 0
        prevPosition[secondPickupRow][secondPickupCol] = 0
        castled = True

    #update position with moved piece in its new spot
    if ((newI is not None) and (newJ is not None)): 
        prevPosition[newI][newJ] = pieceMoved
        if ((pieceMoved == 'P' or pieceMoved == 'p') and (newI == 0 or newI == 7)):
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
            

def pieceMoved(prevPosition, firstPickupRow, firstPickupCol, secondArr):
    #variable declaration
    file = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    currSquare = None
    newSquare = None
    pieceMoved = None
    newI = None
    newJ = None

    #if first array is 0 and previous position isn't, that's the piece that's moved
    if prevPosition[firstPickupRow][firstPickupCol] != 0:
        pieceMoved = prevPosition[firstPickupRow][firstPickupCol]
        currSquare = file[firstPickupCol] + str(8 - firstPickupRow)
        prevPosition[firstPickupRow][firstPickupCol] = 0

    for i in range(8):
        for j in range(8):
            #if second array is 1 and first array isn't, then that's the new square
            if secondArr[i][j] == 1 and prevPosition[i][j] == 0:
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

    device_info = find_device()
    if not device_info:
        print(f"Device with VID:{VENDOR_ID:04x} and PID:{PRODUCT_ID:04x} not found")
        return

    try:
        h = hid.device()
        h.open(VENDOR_ID, PRODUCT_ID)
        
        print(f"Opened device: {h.get_manufacturer_string()} {h.get_product_string()}")
        

        #TODO: MAKE REPORT TO RESTART GAME????????????????????????????????????????????????????????!!!!!!!!!!!!!!!!!!!!!!!
        #start a game:
        board = chess.Board()

        
        while True:
            try:
                # Read the report
                data = h.read(69, timeout_ms=1000)  # Adjust size if needed
                if data:
                    report_id = data[0]
                    if report_id == 1:
                        report1 = HIDClockModeReports.from_bytes(data)
                        print(report1)
                        currSquare, newSquare = pieceMoved(initialPosition, report1.firstPickupRow, report1.firstPickupCol, report1.secondPickupState)
                        moveStr = currSquare + newSquare
                        board.push_uci(moveStr)
                        print(board)
                        print('\n')
                    elif report_id == 2:
                        report2 = HIDClockModeReports.from_bytes(data)
                        print(report2)  # 3 sets of pickup data
                        currSquare, newSquare = takenPiece(board, initialPosition, report2.firstPickupRow, report2.firstPickupCol, report2.secondPickupRow, report2.secondPickupCol, report2.thirdPickupState)
                        moveStr = currSquare + newSquare
                        board.push_uci(moveStr)
                        print(board)
                        print('\n')
                    else:
                        print(f"Unknown Report ID: {report_id}")
                time.sleep(0.1)  # Small delay to prevent tight looping
            except IOError as e:
                print(f"IOError: {str(e)}")
                time.sleep(1)  # Wait a bit before retrying
    except IOError as e:
        print(f"Unable to open device: {str(e)}")
    finally:
        h.close()





    print(chess.__file__)
    # first move
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
    
    firstMoveRow = 6
    firstMoveCol = 4


    # second move
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
    
    secondMoveRow = 1
    secondMoveCol = 4

    #third move
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

    thirdMoveRow = 7
    thirdMoveCol = 6

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

    fourthMoveRow = 0
    fourthMoveCol = 1

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

    fifthMoveRow = 3
    fifthMoveCol = 4

    fifthMoveRow2 = 5
    fifthMoveCol2 = 5


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
    sixthMoveRow = 2
    sixthMoveCol = 2
    sixthMoveRow2 = 3
    sixthMoveCol2 = 4
    
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
    
    seventhMoveRow = 7
    seventhMoveCol = 5
    
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

    eighthMoveRow = 0
    eighthMoveCol = 5
    
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

    ninethMoveRow = 7
    ninethMoveCol = 4
    ninethMoveRow2 = 7
    ninethMoveCol2 = 7
    
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
    tenthMoveRow = 0
    tenthMoveCol = 6
    
    # arr22 = [[1, 0, 1, 1, 1, 0, 0, 1],
    # 		[1, 1, 1, 1, 1, 1, 1, 1],
    # 		[0, 0, 0, 0, 0, 0, 0, 0],
    # 		[0, 0, 0, 0, 1, 0, 0, 0],
    # 		[0, 0, 0, 0, 1, 0, 0, 0],
    # 		[0, 0, 0, 0, 0, 0, 0, 0],
    # 		[1, 1, 1, 1, 1, 1, 1, 1],
    # 		[1, 1, 1, 1, 0, 1, 1, 0],
    # 		]
    
    # arr23 = [[1, 0, 1, 1, 1, 0, 0, 1],
    # 		[1, 1, 1, 1, 1, 1, 1, 1],
    # 		[0, 0, 0, 0, 0, 1, 0, 0],
    # 		[0, 0, 0, 0, 1, 0, 0, 0],
    # 		[0, 0, 0, 0, 1, 0, 0, 0],
    # 		[0, 0, 0, 0, 0, 0, 0, 0],
    # 		[1, 1, 1, 1, 1, 1, 1, 1],
    # 		[1, 1, 1, 1, 0, 1, 1, 0],
    # 		]
    
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
    eleventhMoveRow = 7
    eleventhMoveCol = 1
    
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
    twelfthMoveRow = 0
    twelfthMoveCol = 7
    twelfthMoveRow2 = 0
    twelfthMoveCol2 = 4
    
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
    thirteenthMoveRow = 6
    thirteenthMoveCol = 1
    
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

    fourteenthMoveRow = 1
    fourteenthMoveCol = 0
    
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
    fifteenthMoveRow = 4
    fifteenthMoveCol = 1
    
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
    sixteenthMoveRow = 1
    sixteenthMoveCol = 7

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

    seventeenthMoveRow = 2
    seventeenthMoveCol = 0
    seventeenthMoveRow2 = 3
    seventeenthMoveCol2 = 1
    
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
    eighteenthMoveRow = 1
    eighteenthMoveCol = 6

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
    nineteenthMoveRow = 1
    nineteenthMoveCol = 1
    nineteenthMoveRow2 = 2
    nineteenthMoveCol2 = 0
    
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

    twentiethMoveRow = 4
    twentiethMoveCol = 4
    twentiethMoveRow2 = 2
    twentiethMoveCol2 = 5
    
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

    twentyFirstMoveRow = 0
    twentyFirstMoveCol = 0
    twentyFirstMoveRow2 = 1
    twentyFirstMoveCol2 = 1


    #start a game:
    board = chess.Board()

    currSquare, newSquare = pieceMoved(initialPosition, 6, 4, arr2)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    # print(currSquare)
    # print(newSquare)
    # printPos(initialPosition)

    currSquare, newSquare = pieceMoved(initialPosition, secondMoveRow, secondMoveCol, arr4)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = pieceMoved(initialPosition, thirdMoveRow, thirdMoveCol, arr6)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = pieceMoved(initialPosition, fourthMoveRow, fourthMoveCol, arr8)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = takenPiece(board, initialPosition, fifthMoveRow, fifthMoveCol, fifthMoveRow2, fifthMoveCol2, arr11)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = takenPiece(board, initialPosition, sixthMoveRow, sixthMoveCol, sixthMoveRow2, sixthMoveCol2, arr14)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = pieceMoved(initialPosition, seventhMoveRow, seventhMoveCol, arr16)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = pieceMoved(initialPosition, eighthMoveRow, eighthMoveCol, arr18)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    # piecePossibleMoves(board, 7, 4)

    currSquare, newSquare = takenPiece(board, initialPosition, ninethMoveRow, ninethMoveCol, ninethMoveRow2, ninethMoveCol2, arr21)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = pieceMoved(initialPosition, tenthMoveRow, tenthMoveCol, arr23)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = pieceMoved(initialPosition, eleventhMoveRow, eleventhMoveCol, arr25)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = takenPiece(board, initialPosition, twelfthMoveRow, twelfthMoveCol, twelfthMoveRow2, twelfthMoveCol2, arr28)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = pieceMoved(initialPosition, thirteenthMoveRow, thirteenthMoveCol, arr30)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = pieceMoved(initialPosition, fourteenthMoveRow, fourteenthMoveCol, arr32)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = pieceMoved(initialPosition, fifteenthMoveRow, fifteenthMoveCol, arr34)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = pieceMoved(initialPosition, sixteenthMoveRow, sixteenthMoveCol, arr36)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = takenPiece(board, initialPosition, seventeenthMoveRow, seventeenthMoveCol, seventeenthMoveRow2, seventeenthMoveCol2, arr39)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = pieceMoved(initialPosition, eighteenthMoveRow, eighteenthMoveCol, arr41)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')
    piecePossibleMoves(board, 6, 4)

    currSquare, newSquare = takenPiece(board, initialPosition, nineteenthMoveRow, nineteenthMoveCol, nineteenthMoveRow2, nineteenthMoveCol2, arr44)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = takenPiece(board, initialPosition, twentiethMoveRow, twentiethMoveCol, twentiethMoveRow2, twentiethMoveCol2, arr47)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = takenPiece(board, initialPosition, twentyFirstMoveRow, twentyFirstMoveCol, twentyFirstMoveRow2, twentyFirstMoveCol2, arr50)
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
    
    firstMoveRow = 7
    firstMoveCol = 1
    
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

    secondMoveRow = 0
    secondMoveCol = 1
    
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

    thirdMoveRow = 6
    thirdMoveCol = 1
    
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

    fourthMoveRow = 1
    fourthMoveCol = 1
    
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

    fifthMoveRow = 7
    fifthMoveCol = 2
    
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

    sixthMoveRow = 0
    sixthMoveCol = 2
    
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
    seventhMoveRow = 6
    seventhMoveCol = 3
    
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
    eighthMoveRow = 1
    eighthMoveCol = 3
    
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
    ninethMoveRow = 7
    ninethMoveCol = 3
    
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
    tenthMoveRow = 0
    tenthMoveCol = 3
    
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

    eleventhMoveRow = 7
    eleventhMoveCol = 0
    eleventhMoveRow2 = 7
    eleventhMoveCol2 = 4
    
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
    twelfthMoveRow = 0
    twelfthMoveCol = 4
    twelfthMoveRow2 = 0
    twelfthMoveCol2 = 0
    
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
    thirteenthMoveRow = 5
    thirteenthMoveCol = 1
    
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
    fourteenthMoveRow = 2
    fourteenthMoveCol = 2
    
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
    fifteenthMoveRow = 4
    fifteenthMoveCol = 1
    
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
    sixteenthMoveRow = 1
    sixteenthMoveCol = 0
    
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
    seventeenthMoveRow = 3
    seventeenthMoveCol = 1
    seventeenthMoveRow = 3
    seventeenthMoveCol = 0
    
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

    eighteenthMoveRow = 1
    eighteenthMoveCol = 6
    
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
    nineteenthMoveRow = 2
    nineteenthMoveCol = 0
    
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
    twentiethMoveRow = 3
    twentiethMoveCol = 6
    
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
    twentyFirstMoveRow = 6
    twentyFirstMoveCol = 5
    
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
    twentySecondMoveRow = 4
    twentySecondMoveCol = 5
    twentySecondMoveRow2 = 4
    twentySecondMoveCol2 = 6
    
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
    twentyThirdMoveRow = 1
    twentyThirdMoveCol = 0
    
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

    twentyFourthMoveRow = 0
    twentyFourthMoveCol = 0
    twentyFourthMoveRow2 = 1
    twentyFourthMoveCol2 = 1
    
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
    twentyFifthMoveRow = 6
    twentyFifthMoveCol = 0
    
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
    twentySixthMoveRow = 6
    twentySixthMoveCol = 6
    twentySixthMoveRow2 = 5
    twentySixthMoveCol2 = 5
    
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
    twentySeventhMoveRow = 5
    twentySeventhMoveCol = 2
    
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

    twentyEighthMoveRow = 6
    twentyEighthMoveCol = 6
    twentyEighthMoveRow2 = 7
    twentyEighthMoveCol2 = 7
    

    
    currSquare, newSquare = pieceMoved(newInitialPosition, firstMoveRow, firstMoveCol, arr2)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, secondMoveRow, secondMoveCol, arr4)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, thirdMoveRow, thirdMoveCol, arr6)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, fourthMoveRow, fourthMoveCol, arr8)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, fifthMoveRow, fifthMoveCol, arr10)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, sixthMoveRow, sixthMoveCol, arr12)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, seventhMoveRow, seventhMoveCol, arr14)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, eighthMoveRow, eighthMoveCol, arr16)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, ninethMoveRow, ninethMoveCol, arr18)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, tenthMoveRow, tenthMoveCol, arr20)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = takenPiece(board2, newInitialPosition, eleventhMoveRow, eleventhMoveCol, eleventhMoveRow2, eleventhMoveCol2, arr23)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = takenPiece(board2, newInitialPosition, twelfthMoveRow, twelfthMoveCol, twelfthMoveRow2, twelfthMoveCol2, arr26)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, thirteenthMoveRow, thirteenthMoveCol, arr28)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, fourteenthMoveRow, fourteenthMoveCol, arr30)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, fifteenthMoveRow, fifteenthMoveCol, arr32)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, sixteenthMoveRow, sixteenthMoveCol, arr34)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')

    currSquare, newSquare = takenPiece(board2, newInitialPosition, seventeenthMoveRow, seventeenthMoveCol, seventeenthMoveRow2, seventeenthMoveCol2, arr37)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, eighteenthMoveRow, eighteenthMoveCol, arr39)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, nineteenthMoveRow, nineteenthMoveCol, arr41)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, twentiethMoveRow, twentiethMoveCol, arr43)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, twentyFirstMoveRow, twentyFirstMoveCol, arr45)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')

    currSquare, newSquare = takenPiece(board2, newInitialPosition, twentySecondMoveRow, twentySecondMoveCol, twentySecondMoveRow2, twentySecondMoveCol2, arr48)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')
    
    currSquare, newSquare = pieceMoved(newInitialPosition, twentyThirdMoveRow, twentyThirdMoveCol, arr50)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')
    
    currSquare, newSquare = takenPiece(board2, newInitialPosition, twentyFourthMoveRow, twentyFourthMoveCol, twentyFourthMoveRow2, twentyFourthMoveCol2, arr53)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, twentyFifthMoveRow, twentyFifthMoveCol, arr55)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')

    currSquare, newSquare = takenPiece(board2, newInitialPosition, twentySixthMoveRow, twentySixthMoveCol, twentySixthMoveRow2, twentySixthMoveCol2, arr58)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, twentySeventhMoveRow, twentySeventhMoveCol, arr60)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')

    currSquare, newSquare = takenPiece(board2, newInitialPosition, twentyEighthMoveRow, twentyEighthMoveCol, twentyEighthMoveRow2, twentyEighthMoveCol2, arr63)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')


if __name__ == '__main__':
		main()