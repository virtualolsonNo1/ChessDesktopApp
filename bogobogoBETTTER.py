

import copy
import random

c = 0

def is_sorted(arr, c):
    c += 1
    print("Unsorted for %s:" % c)
    print(arr)
    if len(arr) <= 1:
        return arr

    lastEl = arr[-1]
    # TODO: IS THIS NECESSARY
    arrCp = copy.deepcopy(arr)
    srtArr = arrCp[0:len(arrCp) - 1]
    srtArr = is_sorted(srtArr, c)
    # print(sorted)
    print("Sorted array")
    print(srtArr)

    print("Comparison value")
    print(lastEl)
    if arr[-1] >= srtArr[-1]:
        # return True, arr
        temp = arr[-1]
        arr = srtArr
        arr.append(temp)
        print("First print!!!")
        print(arr)
        return arr
    else:
        random.shuffle(arr)
        print("SHUFFLING!!!!!!")
        print(arr)
        return is_sorted(arr, c)



def main():
    arr = [5, 4, 3, 2, 1, 7, 6, 8]
    random.shuffle(arr)
    arr = is_sorted(arr, c)
    # sorted
    print("Sorted for %s:" % c)
    print(arr)
    print("Final sorted arr: ")
    print(arr)

main()