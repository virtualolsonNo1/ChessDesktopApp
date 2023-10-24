#No take shit
            
def UpdatePositionNoTake(newArr, prevPosition):
    piece = None
    newI = None
    newJ = None
    for i in range(0, 8):
        for j in range(0, 8):
            if newArr[i][j] == 0 and prevPosition[i][j] != 0:
                piece = prevPosition[i][j]
                prevPosition[i][j] = 0
            elif newArr[i][j] == 1 and prevPosition[i][j] == 0:
                newI = i
                newJ = j
    prevPosition[newI][newJ] = piece



def calculateMoveNoTake(prevArr, currArr):
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