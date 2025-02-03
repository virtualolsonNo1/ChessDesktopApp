import copy
import random
import time
import sys

c = 0

def is_sorted(arr):
    if len(arr) <= 1:
        return arr

    arrCp = copy.deepcopy(arr)
    arrCp[0:-1] = is_sorted(arrCp[0:-1])
    if arrCp[-1] >= max(arrCp[0:-1]):
        if arr == arrCp:
            return arrCp
        else:
            random.shuffle(arrCp)
            return is_sorted(arrCp)
    else:
        random.shuffle(arrCp)
        return is_sorted(arrCp)



def main():
    # Check current limit
    print("Current recursion limit:", sys.getrecursionlimit())  # Default is usually 1000

    # Set a new limit (for example, 5000)
    sys.setrecursionlimit(20000)

    print("New recursion limit:", sys.getrecursionlimit())
    
    average = 0
    for i in range(40):
        arr = [1, 2, 3, 4, 5, 6]
        random.shuffle(arr)
        currTime = time.time()
        arr = is_sorted(arr)
        newTime = time.time()
        # sorted
        # print("Sorted for %s:" % c)
        # print(arr)
        print("Final sorted arr: ")
        print(arr)
        print(newTime - currTime)
        average += newTime - currTime

    print(average / 40)
main()