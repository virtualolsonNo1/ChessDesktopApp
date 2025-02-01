import copy
import random

c = 0

def is_sorted(arr, c):
    c += 1
    print("Unsorted for %s:" % c)
    print(arr)
    if len(arr) <= 1:
        return arr
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
        # srtArr.append(len(arr) - 1)
        # arr = srtArr        
        # return False, arr
        while arr[len(arr) - 1] < srtArr[len(srtArr) - 1]:
            random.shuffle(arr)
            print("SHUFFLING!!!!!!")
            print(arr)
            arrCp = copy.deepcopy(arr)
            srtArr = arrCp[0:len(arrCp) - 1]
            # random.shuffle(arr)
            # print("SHUFFLING!!!!!!")
            srtArr = is_sorted(arr, c)

        temp = arr[len(arr) - 1]
        arr = srtArr
        arr.append(temp)
        print("After while print!!!")
        print(arr)
        return arr
        

# def bgbgsort(arr, c):
#     # while(not is_sorted(arr, c)):
#     #     print("about to shuffle arr: ")
#     #     print(arr)
#     #     print("shuffle")
#     #     random.shuffle(arr)
#     arr = is_sorted(arr, c)
#     # sorted
#     print("Sorted for %s:" % c)
#     print(arr)
    
    
#     return arr


def main():
    arr = [5, 4, 3, 2, 1]
    arr = is_sorted(arr, c)
    # sorted
    print("Sorted for %s:" % c)
    print(arr)
    print("Final sorted arr: ")
    print(arr)

main()

# Unsorted for 1:
# [2, 1, 3]
# Unsorted for 2:
# [2, 1]
# Unsorted for 3:
# [2]
# Sorted for 2:
# [2]
# shuffle
# Unsorted for 2:
# [2, 1]
# Unsorted for 3:
# [2]
# Sorted for 2:
# [2]
# shuffle
# Unsorted for 2:
# [1, 2]
# Unsorted for 3:
# [1]
# Sorted for 2:
# [1]
# Sorted for 1:
# [1, 2]
# Sorted for 0:
# [2, 1, 3]
# PS C:\Users\virtu\Downloads\Projects\ChessDesktopApp> ^C
# PS C:\Users\virtu\Downloads\Projects\ChessDesktopApp> 
# PS C:\Users\virtu\Downloads\Projects\ChessDesktopApp>  c:; cd 'c:\Users\virtu\Downloads\Projects\ChessDesktopApp'; & 'c:\Users\virtu\AppData\Local\Programs\Python\Python313\python.exe' 'c:\Users\virtu\.vscode\extensions\ms-python.debugpy-2024.14.0-win32-x64\bundled\libs\debugpy\adapter/../..\debugpy\launcher' '64900' '--' 'c:\Users\virtu\Downloads\Projects\ChessDesktopApp\bogobogo.py'
# Unsorted for 1:
# [2, 1, 3]
# Unsorted for 2:
# [2, 1]
# Unsorted for 3:
# [2]
# Sorted for 2:
# [2]
# shuffle
# Unsorted for 2:
# [2, 1]
# Unsorted for 3:
# [2]
# Sorted for 2:
# [2]
# shuffle
# Unsorted for 2:
# [1, 2]
# Unsorted for 3:
# [1]
# Sorted for 2:
# [1]
# Sorted for 1:
# [1, 2]
# Sorted for 0:
# [2, 1, 3]
# Final sorted arr:
# [2, 1, 3]