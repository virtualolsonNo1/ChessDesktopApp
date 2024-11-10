import chess
from chess import Board
# import serial
import copy
import hid
import time
from hidFuncs import find_device, VENDOR_ID, PRODUCT_ID
import struct
from analysis import open_game_in_chesscom

class HIDClockModeReports:
    def __init__(self):
        self.reportId = 0
        self.firstPickupRow = 0
        self.firstPickupCol = 0
        self.secondPickupRow = 0
        self.secondPickupCol = 0
        self.finalPickupRow = 0
        self.finalPickupCol = 0

    @classmethod
    def from_bytes(cls, data):
        report = cls()
        data_bytes = bytes(data)  # Convert list to bytes
        report.reportId, report.firstPickupRow, report.firstPickupCol = struct.unpack('<BBB', data_bytes[:3])
        if report.reportId == 1:
            report.finalPickupRow, report.finalPickupCol = struct.unpack('<BB', data_bytes[3:5])
        elif report.reportId == 2:
            # For Report 2, unpack secondPickupCol, secondPickupRow, and thirdPickupState
            report.secondPickupRow, report.secondPickupCol, report.finalPickupRow, report.finalPickupCol  = struct.unpack('<BBBB', data_bytes[3:7])
        
        return report

    def __str__(self):
        if self.reportId == 1:
            return f"Report 1: firstPickup({self.firstPickupRow}, {self.firstPickupCol}), finalData({self.finalPickupRow, self.finalPickupCol})"
        elif self.reportId == 2:
            return f"Report 2: firstPickup({self.firstPickupRow}, {self.firstPickupCol}), secondPickup({self.secondPickupRow}, {self.secondPickupCol}), finalData: ({self.finalPickupRow, self.finalPickupCol})"
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

initialPositionCopy = [['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
			['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
			[0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0],
			['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
			['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
			]

lastPosition = None

def can_be_taken_en_passant(board: chess.Board, square: chess.Square) -> bool:
    """
    Check if the pawn on the given square could be captured by en passant.
    
    Args:
        board: A chess.Board instance representing the current position
        square: The square to check (chess.Square)
    
    Returns:
        bool: True if the pawn can be captured en passant, False otherwise
    """
    # First, check if there's actually a pawn on the square
    piece = board.piece_at(square)
    if piece is None or piece.piece_type != chess.PAWN:
        return False
    
    # Check if the pawn is on the correct rank for en passant
    rank = chess.square_rank(square)
    if (piece.color == chess.WHITE and rank != 3) or \
       (piece.color == chess.BLACK and rank != 4):
        return False
    
    # Check if this pawn just moved two squares
    # This can be verified by checking if the en passant square is adjacent
    ep_square = board.ep_square
    if ep_square is None:
        return False
    
    # The en passant square must be directly behind the pawn
    file = chess.square_file(square)
    ep_file = chess.square_file(ep_square)
    
    return file == ep_file

def piecePossibleMoves(board, pieceI, pieceJ):
    file = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    pieceSquare = file[pieceJ] + str(8 - pieceI)

    legal_moves = list(board.legal_moves)

    if (board.turn == chess.WHITE and initialPosition[pieceI][pieceJ].isupper() or board.turn == chess.BLACK and initialPosition[pieceI][pieceJ].islower()):
        isPlayersPiece = True
        valid_moves = [move for move in legal_moves if pieceSquare in chess.square_name(move.from_square)]
    else:
        isPlayersPiece = False
        valid_moves = [move for move in legal_moves if pieceSquare in chess.square_name(move.to_square)]
        # special handling for en passant
        if board.ep_square is not None and ((board.turn == chess.WHITE and chess.square_rank(board.ep_square) == 7 - (pieceI - 1) and chess.square_file(board.ep_square) == pieceJ) or (board.turn == chess.BLACK and chess.square_rank(board.ep_square) == 7 - (pieceI + 1) and chess.square_file(board.ep_square) == pieceJ)):
            ep_square = chess.square_name(board.ep_square)
            rank = 8 - pieceI
            # For white's turn, the capturable pawn must be on rank 5
            # For black's turn, the capturable pawn must be on rank 4
            if ((board.turn == chess.WHITE and rank == 5) or 
                (board.turn == chess.BLACK and rank == 4)):
                # Find en passant moves where this pawn would be captured
                ep_moves = [move for move in legal_moves 
                          if board.is_en_passant(move) and 
                          chess.square_name(move.to_square) == ep_square]
                valid_moves.extend(ep_moves)
    
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
        if isPlayersPiece == True:
            empty_board[7 - chess.square_rank(move.to_square)][chess.square_file(move.to_square)] = 1

            # if en passant is possible and pawn taking is picked up, light up the pawn to be taken's square and the destination square
            if board.is_en_passant(move):
                # light up square of piece to be taken but not square to move to, as it's not a possible move yet
                empty_board[7 - chess.square_rank(move.to_square)][chess.square_file(move.to_square)] = 0
                if board.turn == chess.WHITE:
                    empty_board[7 - chess.square_rank(move.to_square) + 1][chess.square_file(move.to_square)] = 1
                else:
                    empty_board[7 - chess.square_rank(move.to_square) - 1][chess.square_file(move.to_square)] = 1
                    
        else:
            # if en passant is possible and pawn to be taken is pick up, light up the taking pawn's square and it's diagonal destination square
            empty_board[7 - chess.square_rank(move.from_square)][chess.square_file(move.from_square)] = 1
    

    rank = 7 - pieceI
    file = pieceJ
    
    move = chess.square(file, rank)
    if len(valid_moves) == 0 and can_be_taken_en_passant(board, move):
        # if en passant is possible and pawn to be taken is pick up, light up the taking pawn's square and it's diagonal destination square
        empty_board[7 - rank][file] = 1
        ep_square = board.ep_square
        empty_board[7 - chess.square_rank(ep_square)][chess.square_file(ep_square)] = 1
        if (file < 7 and ((initialPosition[7 - rank][file + 1] == 'P' and board.turn == chess.WHITE) or (initialPosition[7 - rank][file + 1] == 'p' and board.turn == chess.BLACK))):
            empty_board[7 - rank][file + 1] = 1
        if (file > 0 and ((initialPosition[7 - rank][file - 1] == 'P' and board.turn == chess.WHITE) or (initialPosition[7 - rank][file - 1] == 'p' and board.turn == chess.BLACK))):
            empty_board[7 - rank][file - 1] = 1

    # if no moves possible with that piece, return error
    if len(valid_moves) == 0:  
        raise chess.IllegalMoveError
            
    # printPos(empty_board)
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

#TODO: PLAN!!!!!
#   - get rid of secondPickupArr and thirdPickupArr
#   - After making move, have desktop app send chess board the updated position
#   - have report for game over from chess board to desktop app
#   - make report for when piece picked up, where desktop app send back lights for possible moves
#   - rest handled on chess board, where it can turn off all LEDs if piece put back down or the led of square it moved onto one of allowed squares

#TODO: LATER AFTER ABOVE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#TODO: add ability to redo move if they send invalid move
#TODO: add no clock mode where it sends move after opponent piece moves???????

#TODO: Look into: SHORT PACKET TERMINATOR, WHAT IS REQUIRED IN REPORT, ETC

#This one's a thiccy...
def takenPiece(board, prevPosition, firstPickupRow, firstPickupCol, secondPickupRow, secondPickupCol, finalPickupRow, finalPickupCol):
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
        if (finalPickupRow < 8 and finalPickupCol < 8 and prevPosition[finalPickupRow][finalPickupCol] == 0):
            #calculate new home for pawn that took en pessant
            if prevPosition[secondPickupRow][secondPickupCol] == 'p':
                # set new square to 1 rank higher than spot opponent pawn was at
                newSquare = file[finalPickupCol] + str(8 - finalPickupRow)
                # newI = secondPickupRow - 1
                # newJ = secondPickupCol
                newI = finalPickupRow
                newJ = finalPickupCol
            else:
                # set new square to 1 rank lower than spot opponent pawn was at
                newSquare = file[finalPickupCol] + str(8 - finalPickupRow)
                # newI = secondPickupRow + 1
                # newJ = secondPickupCol
                newI = finalPickupRow
                newJ = finalPickupCol
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
            

def pieceMoved(prevPosition, firstPickupRow, firstPickupCol, finalPickupRow, finalPickupCol):
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

    if prevPosition[finalPickupRow][finalPickupCol] != 1:
        newSquare = file[finalPickupCol] + str(8 - finalPickupRow)
        newI = finalPickupRow
        newJ = finalPickupCol

    if newI is not None and newJ is not None:
            prevPosition[newI][newJ] = pieceMoved
            if (pieceMoved == 'P' or pieceMoved == 'p') and (newI == 0 or newI == 7):
                    newSquare += 'q'

    return currSquare, newSquare




def main():
    global initialPosition

    device_info = find_device()
    while not device_info:
        device_info = find_device()
        print(f"Device with VID:{VENDOR_ID:04x} and PID:{PRODUCT_ID:04x} not found")
        time.sleep(1)

    board = chess.Board()

    try:
        while True:
            try:
                h = hid.device()
                h.open(VENDOR_ID, PRODUCT_ID)
                
                print(f"Opened device: {h.get_manufacturer_string()} {h.get_product_string()}")
                

                #start a game:

                while True:
                    # try:
                    # Read the report
                    data = h.read(7)  # Adjust size if needed
                    if data:
                        report_id = data[0]
                        print(f"REPORT ID: {report_id}")
                        prevPrevPosition = copy.deepcopy(initialPosition)
                        if report_id == 1:
                            report1 = HIDClockModeReports.from_bytes(data)
                            print(report1)
                            try:
                                currSquare, newSquare = pieceMoved(initialPosition, report1.firstPickupRow, report1.firstPickupCol, report1.finalPickupRow, report1.finalPickupCol)
                                moveStr = currSquare + newSquare
                                board.push_uci(moveStr)
                                print(board)
                                print('\n')
                                flattened_array = [item for sublist in initialPosition for item in sublist]
                                flattened_array.insert(0, 5)
                                byte_array = bytearray(ord(x) if isinstance(x, str) else x for x in flattened_array)
                                bytes_written = h.write(byte_array)
                                if bytes_written == -1:
                                    print("Error: Unable to write to device")
                                    print(f"Last error: {h.error()}")
                            except (chess.IllegalMoveError, TypeError, AttributeError, IndexError) as e:
                                initialPosition = copy.deepcopy(prevPrevPosition)
                                bytes = [6, 255]
                                bytes_written = h.write(bytes)
                                # Catches errors that might occur during string concatenation
                                print(f"Error in move name: {type(e).__name__}")
                                print(f"Error message: {str(e)}")
                                    
                        elif report_id == 2:
                            report2 = HIDClockModeReports.from_bytes(data)
                            print(report2)  # 3 sets of pickup data
                            currSquare, newSquare = takenPiece(board, initialPosition, report2.firstPickupRow, report2.firstPickupCol, report2.secondPickupRow, report2.secondPickupCol, report2.finalPickupRow, report2.finalPickupCol)
                            try:
                                moveStr = currSquare + newSquare
                                board.push_uci(moveStr)
                                print(board)
                                print('\n')
                                flattened_array = [item for sublist in initialPosition for item in sublist]
                                flattened_array.insert(0, 5)
                                byte_array = bytearray(ord(x) if isinstance(x, str) else x for x in flattened_array)
                                bytes_written = h.write(byte_array)
                                if bytes_written == -1:
                                    print("Error: Unable to write to device")
                                    print(f"Last error: {h.error()}")
                            except (chess.IllegalMoveError, TypeError, AttributeError) as e:
                                initialPosition = copy.deepcopy(prevPrevPosition)
                                bytes = [6, 255]
                                bytes_written = h.write(bytes)
                                # Catches errors that might occur during string concatenation
                                print(f"Error in move name: {type(e).__name__}")
                                print(f"Error message: {str(e)}")
                                
                        elif report_id == 3:
                            if (data[1] == 255):
                                # TODO: TEST THIS SHIT!!!!!!!!!!!!!!!!!!!!!!
                                open_game_in_chesscom(board)
                                board.reset()
                                initialPosition = copy.deepcopy(initialPositionCopy)
                                print("RESET GAME")
                            else: 
                                pieceI = data[1] >> 3
                                pieceJ = data[1] & 0x7
                                print("LIGHTS")
                                try:
                                    lights = piecePossibleMoves(board, pieceI, pieceJ)
                                except (chess.IllegalMoveError, TypeError, AttributeError) as e:
                                    initialPosition = copy.deepcopy(prevPrevPosition)
                                    bytes = [6, 255]
                                    bytes_written = h.write(bytes)
                                    # Catches errors that might occur during string concatenation
                                    print(f"Error in move name: {type(e).__name__}")
                                    print(f"Error message: {str(e)}")
                                    continue
                                flattened_array = [item for sublist in lights for item in sublist]
                                flattened_array.insert(0, 4)
                                bytes_written = h.write(flattened_array)
                                print(f"Bytes Written: {bytes_written}")
                                if bytes_written == -1:
                                    print("Error: Unable to write to device")
                                    print(f"Last error: {h.error()}")
                        else:
                            print(f"Unknown Report ID: {report_id}")
                    # time.sleep(0.1)  # Small delay to prevent tight looping
                    # except IOError as e:
                    #     print(f"IOError: {str(e)}")
                    #     break
            except IOError as e:
                print(f"Failed to connect to the device: {str(e)}")
                print("Retrying in 1 seconds...")
                time.sleep(2)
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
    firstMoveRow2 = 4
    firstMoveCol2 = 4


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
    secondMoveRow2 = 3
    secondMoveCol2 = 4

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
    thirdMoveRow2 = 5
    thirdMoveCol2 = 5

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
    fourthMoveRow2 = 2
    fourthMoveCol2 = 2

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
    
    fifthMoveRow3 = 8
    fifthMoveCol3 = 8


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
    sixthMoveRow3 = 8
    sixthMoveCol3 = 8
    
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
    seventhMoveRow2 = 6
    seventhMoveCol2 = 4
    
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
    eighthMoveRow2 = 1
    eighthMoveCol2 = 4
    
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
    ninethMoveRow3 = 8
    ninethMoveCol3 = 8
    
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
    tenthMoveRow2 = 2
    tenthMoveCol2 = 5
    
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
    eleventhMoveRow2 = 5
    eleventhMoveCol2 = 2
    
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
    twelfthMoveRow3 = 8
    twelfthMoveCol3 = 8
    
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
    thirteenthMoveRow2 = 4
    thirteenthMoveCol2 = 1
    
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
    fourteenthMoveRow2 = 2
    fourteenthMoveCol2 = 0
    
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
    fifteenthMoveRow2 = 3
    fifteenthMoveCol2 = 1
    
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
    sixteenthMoveRow2 = 2
    sixteenthMoveCol2 = 7

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
    seventeenthMoveRow3 = 8
    seventeenthMoveCol3 = 8
    
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
    eighteenthMoveRow2 = 2
    eighteenthMoveCol2 = 6

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
    nineteenthMoveRow3 = 8
    nineteenthMoveCol3 = 8
    
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
    twentiethMoveRow3 = 8
    twentiethMoveCol3 = 8
    
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
    twentyFirstMoveRow3 = 8
    twentyFirstMoveCol3 = 8


    #start a game:
    board = chess.Board()

    currSquare, newSquare = pieceMoved(initialPosition, 6, 4, firstMoveRow2, firstMoveCol2)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    # print(currSquare)
    # print(newSquare)
    # printPos(initialPosition)

    currSquare, newSquare = pieceMoved(initialPosition, secondMoveRow, secondMoveCol, secondMoveRow2, secondMoveCol2)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = pieceMoved(initialPosition, thirdMoveRow, thirdMoveCol, thirdMoveRow2, thirdMoveCol2)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = pieceMoved(initialPosition, fourthMoveRow, fourthMoveCol, fourthMoveRow2, fourthMoveCol2)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = takenPiece(board, initialPosition, fifthMoveRow, fifthMoveCol, fifthMoveRow2, fifthMoveCol2, fifthMoveRow3, fifthMoveCol3)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = takenPiece(board, initialPosition, sixthMoveRow, sixthMoveCol, sixthMoveRow2, sixthMoveCol2, sixthMoveRow3, sixthMoveCol3)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = pieceMoved(initialPosition, seventhMoveRow, seventhMoveCol, seventhMoveRow2, seventhMoveCol2)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = pieceMoved(initialPosition, eighthMoveRow, eighthMoveCol, eighthMoveRow2, eighthMoveCol2)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    # piecePossibleMoves(board, 7, 4)

    currSquare, newSquare = takenPiece(board, initialPosition, ninethMoveRow, ninethMoveCol, ninethMoveRow2, ninethMoveCol2, ninethMoveRow3, ninethMoveCol3)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = pieceMoved(initialPosition, tenthMoveRow, tenthMoveCol, tenthMoveRow2, tenthMoveCol2)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = pieceMoved(initialPosition, eleventhMoveRow, eleventhMoveCol, eleventhMoveRow2, eleventhMoveCol2)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = takenPiece(board, initialPosition, twelfthMoveRow, twelfthMoveCol, twelfthMoveRow2, twelfthMoveCol2, twelfthMoveRow3, twelfthMoveCol3)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = pieceMoved(initialPosition, thirteenthMoveRow, thirteenthMoveCol, thirteenthMoveRow2, thirteenthMoveCol2)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = pieceMoved(initialPosition, fourteenthMoveRow, fourteenthMoveCol, fourteenthMoveRow2, fourteenthMoveCol2)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = pieceMoved(initialPosition, fifteenthMoveRow, fifteenthMoveCol, fifteenthMoveRow2, fifteenthMoveCol2)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = pieceMoved(initialPosition, sixteenthMoveRow, sixteenthMoveCol, sixteenthMoveRow2, sixteenthMoveCol2)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = takenPiece(board, initialPosition, seventeenthMoveRow, seventeenthMoveCol, seventeenthMoveRow2, seventeenthMoveCol2, seventeenthMoveRow3, seventeenthMoveCol3)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = pieceMoved(initialPosition, eighteenthMoveRow, eighteenthMoveCol, eighteenthMoveRow2, eighteenthMoveCol2)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')
    piecePossibleMoves(board, 6, 4)

    currSquare, newSquare = takenPiece(board, initialPosition, nineteenthMoveRow, nineteenthMoveCol, nineteenthMoveRow2, nineteenthMoveCol2, nineteenthMoveRow3, nineteenthMoveCol3)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = takenPiece(board, initialPosition, twentiethMoveRow, twentiethMoveCol, twentiethMoveRow2, twentiethMoveCol2, twentiethMoveRow3, twentiethMoveCol3)
    moveStr = currSquare + newSquare
    board.push_uci(moveStr)
    print(board)
    print('\n')

    currSquare, newSquare = takenPiece(board, initialPosition, twentyFirstMoveRow, twentyFirstMoveCol, twentyFirstMoveRow2, twentyFirstMoveCol2, twentyFirstMoveRow3, twentyFirstMoveCol3)
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
    firstMoveRow2 = 5
    firstMoveCol2 = 2
    
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
    secondMoveRow2 = 2
    secondMoveCol2 = 2
    
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
    thirdMoveRow2 = 5
    thirdMoveCol2 = 1
    
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
    fourthMoveRow2 = 2
    fourthMoveCol2 = 1
    
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
    fifthMoveRow2 = 6
    fifthMoveCol2 = 1
    
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
    sixthMoveRow2 = 1
    sixthMoveCol2 = 1
    
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
    seventhMoveRow2 = 5
    seventhMoveCol2 = 3
    
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
    eighthMoveRow2 = 2
    eighthMoveCol2 = 3
    
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
    ninethMoveRow2 = 6
    ninethMoveCol2 = 3
    
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
    tenthMoveRow2 = 1
    tenthMoveCol2 = 3
    
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
    eleventhMoveRow3 = 8
    eleventhMoveCol3 = 8
    
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
    twelfthMoveRow3 = 8
    twelfthMoveCol3 = 8
    
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
    thirteenthMoveRow2 = 4
    thirteenthMoveCol2 = 1
    
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
    fourteenthMoveRow2 = 3
    fourteenthMoveCol2 = 4
    
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
    fifteenthMoveRow2 = 3
    fifteenthMoveCol2 = 1
    
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
    sixteenthMoveRow2 = 3
    sixteenthMoveCol2 = 0
    
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
    seventeenthMoveRow2 = 3
    seventeenthMoveCol2 = 0
    seventeenthMoveRow3 = 2
    seventeenthMoveCol3 = 0
    
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
    eighteenthMoveRow2 = 3
    eighteenthMoveCol2 = 6
    
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
    nineteenthMoveRow2 = 1
    nineteenthMoveCol2 = 0
    
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
    twentiethMoveRow2 = 4
    twentiethMoveCol2 = 6
    
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
    twentyFirstMoveRow2 = 4
    twentyFirstMoveCol2 = 5
    
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
    twentySecondMoveRow3 = 5
    twentySecondMoveCol3 = 5
    
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
    twentyThirdMoveRow2 = 0
    twentyThirdMoveCol2 = 0
    
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
    twentyFourthMoveRow3 = 8
    twentyFourthMoveCol3 = 8
    
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
    twentyFifthMoveRow2 = 5
    twentyFifthMoveCol2 = 0
    
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
    twentySixthMoveRow3 = 8
    twentySixthMoveCol3 = 8
    
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
    twentySeventhMoveRow2 = 3
    twentySeventhMoveCol2 = 3
    
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
    twentyEighthMoveRow3 = 8
    twentyEighthMoveCol3 = 8
    

    
    currSquare, newSquare = pieceMoved(newInitialPosition, firstMoveRow, firstMoveCol, firstMoveRow2, firstMoveCol2)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, secondMoveRow, secondMoveCol, secondMoveRow2, secondMoveCol2)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, thirdMoveRow, thirdMoveCol, thirdMoveRow2, thirdMoveCol2)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, fourthMoveRow, fourthMoveCol, fourthMoveRow2, fourthMoveCol2)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, fifthMoveRow, fifthMoveCol, fifthMoveRow2, fifthMoveCol2)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, sixthMoveRow, sixthMoveCol, sixthMoveRow2, sixthMoveCol2)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, seventhMoveRow, seventhMoveCol, seventhMoveRow2, seventhMoveCol2)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, eighthMoveRow, eighthMoveCol, eighthMoveRow2, eighthMoveCol2)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, ninethMoveRow, ninethMoveCol, ninethMoveRow2, ninethMoveCol2)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, tenthMoveRow, tenthMoveCol, tenthMoveRow2, tenthMoveCol2)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = takenPiece(board2, newInitialPosition, eleventhMoveRow, eleventhMoveCol, eleventhMoveRow2, eleventhMoveCol2, eleventhMoveRow3, eleventhMoveCol3)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = takenPiece(board2, newInitialPosition, twelfthMoveRow, twelfthMoveCol, twelfthMoveRow2, twelfthMoveCol2, twelfthMoveRow3, twelfthMoveCol3)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, thirteenthMoveRow, thirteenthMoveCol, thirteenthMoveRow2, thirteenthMoveCol2)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, fourteenthMoveRow, fourteenthMoveCol, fourteenthMoveRow2, fourteenthMoveCol2)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, fifteenthMoveRow, fifteenthMoveCol, fifteenthMoveRow2, fifteenthMoveCol2)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print(newInitialPosition)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, sixteenthMoveRow, sixteenthMoveCol, sixteenthMoveRow2, sixteenthMoveCol2)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')

    currSquare, newSquare = takenPiece(board2, newInitialPosition, seventeenthMoveRow, seventeenthMoveCol, seventeenthMoveRow2, seventeenthMoveCol2, seventeenthMoveRow3, seventeenthMoveCol3)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, eighteenthMoveRow, eighteenthMoveCol, eighteenthMoveRow2, eighteenthMoveCol2)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, nineteenthMoveRow, nineteenthMoveCol, nineteenthMoveRow2, nineteenthMoveCol2)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, twentiethMoveRow, twentiethMoveCol, twentiethMoveRow2, twentiethMoveCol2)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, twentyFirstMoveRow, twentyFirstMoveCol, twentyFirstMoveRow2, twentyFirstMoveCol2)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')

    currSquare, newSquare = takenPiece(board2, newInitialPosition, twentySecondMoveRow, twentySecondMoveCol, twentySecondMoveRow2, twentySecondMoveCol2, twentySecondMoveRow3, twentySecondMoveCol3)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')
    
    currSquare, newSquare = pieceMoved(newInitialPosition, twentyThirdMoveRow, twentyThirdMoveCol, twentyThirdMoveRow2, twentyThirdMoveCol2)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')
    
    currSquare, newSquare = takenPiece(board2, newInitialPosition, twentyFourthMoveRow, twentyFourthMoveCol, twentyFourthMoveRow2, twentyFourthMoveCol2, twentyFourthMoveRow3, twentyFourthMoveCol3)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, twentyFifthMoveRow, twentyFifthMoveCol, twentyFifthMoveRow2, twentyFifthMoveCol2)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')

    currSquare, newSquare = takenPiece(board2, newInitialPosition, twentySixthMoveRow, twentySixthMoveCol, twentySixthMoveRow2, twentySixthMoveCol2, twentySixthMoveRow3, twentySixthMoveCol3)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')

    currSquare, newSquare = pieceMoved(newInitialPosition, twentySeventhMoveRow, twentySeventhMoveCol, twentySeventhMoveRow2, twentySeventhMoveCol2)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')

    currSquare, newSquare = takenPiece(board2, newInitialPosition, twentyEighthMoveRow, twentyEighthMoveCol, twentyEighthMoveRow2, twentyEighthMoveCol2, twentyEighthMoveRow3, twentyEighthMoveCol3)
    moveStr = currSquare + newSquare
    board2.push_uci(moveStr)
    print(board2)
    print('\n')


if __name__ == '__main__':
		main()