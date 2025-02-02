

import copy
import random
import time

c = 0

def bogobogo(arr):
    if len(arr) <= 1:
        return arr

    arrCp = copy.deepcopy(arr)

    while (True):

        arrCp[0:-1] = bogobogo(arrCp[0:-1])

        if arrCp[-1] >= arrCp[-2]:
            #TODO: CHECK IF ORDER IS EQUAL TO INITIAL ARRAY!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            return arrCp
        else:
            random.shuffle(arrCp)



def main():
    arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    random.shuffle(arr)
    currTime = time.time()
    arr = bogobogo(arr)
    postTime = time.time()
    # sorted
    print(postTime - currTime)
    print("Final sorted arr: ")
    print(arr)

main()