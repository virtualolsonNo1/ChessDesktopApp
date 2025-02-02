import copy
import random
import time

c = 0

def is_sorted(arr):
    if len(arr) <= 1:
        return arr

    arrCp = copy.deepcopy(arr)
    arrCp[0:-1] = is_sorted(arrCp[0:-1])
    if arrCp[-1] >= arrCp[-2]:
        return arrCp
    else:
        random.shuffle(arrCp)
        return is_sorted(arrCp)



def main():
    arr = [1, 2, 3, 4, 5, 6, 7, 8, 9]
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

main()