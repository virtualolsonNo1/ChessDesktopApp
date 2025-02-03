

import sys
import copy
import random
import time

c = 0

def bogobogo(arr):
    if len(arr) <= 1:
        return arr

    arrCp = copy.deepcopy(arr)


    sortCp = bogobogo(arrCp[0:-1])

    if sortCp[-1] > max(arrCp[0:-1]):
        if arrCp[0:-1] == sortCp:
            return arrCp
        else:
            random.shuffle(arrCp)
            return bogobogo(arrCp)
    else:
        random.shuffle(arrCp)
        return bogobogo(arrCp)



def main():
    print("Current recursion limit:", sys.getrecursionlimit())  # Default is usually 1000

    # Set a new limit (for example, 5000)
    sys.setrecursionlimit(100000)

    print("New recursion limit:", sys.getrecursionlimit())
    arr = [1, 2, 3]
    average = 0
    for i in range(40):
        random.shuffle(arr)
        currTime = time.time()
        arr = bogobogo(arr)
        postTime = time.time()
        # sorted
        print(postTime - currTime)
        print("Final sorted arr: ")
        print(arr)
        average += postTime - currTime
    print(average / 40)

main()