
import copy
import random

c = 0

def is_sorted(arr, c):
    c += 1
    print("Unsorted for %s:" % c)
    print(arr)
    if len(arr) <= 1:
        return arr
    while (True):

        lastEl = arr[len(arr) - 1]
        arrCp = copy.deepcopy(arr)
        srtArr = arrCp[0:len(arrCp) - 1]
        srtArr = is_sorted(srtArr, c)
        # print(sorted)
        # print(arr)
        if arr[len(arr) - 1] >= srtArr[len(srtArr) - 1]:

            # return True, arr
            temp = arr[len(arr) - 1]
            arr = srtArr
            arr.append(temp)
            print("First print!!!")
            print(arr)
            return arr
        else:
            print(arr)
            random.shuffle(arr)
            print("SHUFFLING!!!!!!")
            print(arr)



def main():
    arr = [5, 4, 3, 2, 1, 7, 6]
    arr = is_sorted(arr, c)
    # sorted
    print("Sorted for %s:" % c)
    print(arr)
    print("Final sorted arr: ")
    print(arr)

main()