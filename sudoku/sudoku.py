#!/usr/bin/env python
# -*- coding:utf-8 -*-

MAX_COL = 9
MAX_ROW = 9

matrice = [[[1,2,3,4,5,6,7,8,9] for x in range(MAX_COL)] for y in range(MAX_ROW)]
matrice_found = [[0 for x in range(MAX_COL)] for y in range(MAX_ROW)]

fileName ="grille3.txt"

def debug(*list):
    #print(list)
    pass

def DisplayMatrix():
    print('#'.ljust(217,'#'))
    for j in range(1, MAX_COL+1):
        line = "# "
        for i in range(1, MAX_ROW+1):
            character = "|"
            if (i % 3) == 0:
                character = "#"
            line += "{:21} {} ".format(matrice[i-1][j-1],character)
        print("{}".format(line))

        if (j  % 3) == 0:
            print('#'.ljust(217,'#'))

def AddValueInMatrix(x, y, v):
    global loop

    debug("AddValueInMatrix: v={} in ({},{})".format(v, x, y))
    # Remove the value in the col
    for i in range(1, MAX_COL+1):
        if i != x:
            if v in matrice[i-1][y-1]:
                matrice[i-1][y-1].remove(v)
                if len(matrice[i-1][y-1]) == 0:
                    print('Error when removing {} from column {} in ({},{})'.format(v, x, i, y))
                    exit(1)
                else:
                    if len(matrice[i-1][y-1]) == 1:
                        AddValueInMatrix(i, y, matrice[i-1][y-1][0])                        

    # Remove the value in the row
    for j in range(1, MAX_ROW+1):
        if j != y:
            if v in matrice[x-1][j-1]:
                matrice[x-1][j-1].remove(v)
                if len(matrice[x-1][j-1]) == 0:
                    print('Error when removing {} from row {} in ({},{})'.format(v, y, x, j))
                    exit(1)
                else:
                    if len(matrice[x-1][j-1]) == 1:
                        AddValueInMatrix(x, j, matrice[x-1][j-1][0])

    # Remove from the block
    min_i = int(x / 3)
    if (x % 3) == 0:
        min_i -= 1
    min_i = min_i * 3 + 1
    min_j = int(y / 3)
    if (y % 3) == 0:
        min_j -= 1
    min_j = min_j * 3 + 1
    for i in range(min_i, min_i+3):
        for j in range(min_j, min_j+3):
            if i!= x and j != y and (v in matrice[i-1][j-1]):
                matrice[i-1][j-1].remove(v)
                if len(matrice[i-1][j-1]) == 0:
                    print('Error when removing {} in ({},{})'.format(v, i, j))
                    exit(1)
                else:
                    if len(matrice[i-1][j-1]) == 1:
                        AddValueInMatrix(i, j, matrice[i-1][j-1][0])

    matrice[x-1][y-1] = [v]
    matrice_found[x-1][y-1] = 1
    loop = True

def RemoveNumberFromOtherBlocksCol(v, col, x, y):
    global loop
    removed = False

    for j in range(1, 9+1):
        if j >= (y * 3 - 2) and j <= (y * 3):
            continue
        if v in matrice[col-1][j-1]:
            matrice[col-1][j-1].remove(v)
            if len(matrice[col-1][j-1]) == 1:
                print("Found new value {} alone in ({},{}) when removing {}".format(matrice[col-1][j-1][0], col, j, v))
                AddValueInMatrix(col, j, matrice[col-1][j-1][0])
            removed = True

    if removed == True:
        #DisplayMatrix()
        loop = True
    return removed

def RemoveNumberFromOtherBlocksRow(v, row, x, y):
    global loop
    removed = False

    for i in range(1, 9+1):
        if i >= (x * 3 - 2) and i <= (x * 3):
            continue
        if v in matrice[i-1][row-1]:
            matrice[i-1][row-1].remove(v)
            if len(matrice[i-1][row-1]) == 1:
                print("Found new value {} alone in {},{}".format(matrice[i-1][row-1][0], i, row))
                AddValueInMatrix(i, row, matrice[i-1][row-1][0])
            removed = True

    if removed == True:
        #DisplayMatrix()
        loop = True
    return removed

def LooksForUniqueColumnRow():
    global loop

    found_changes = False
    loop = False

    for i in range(0, 3):
        for j in range(0, 3):
            for v in range(1, 9+1):
                found_row = 0
                row = 0
                found_col = 0
                col = 0
                cond = True

                col = 0
                x = i * 3 + 1
                y = j * 3 + 1

                while cond == True:
                    debug('Spy 5', v, x, y, matrice[x-1][y-1])

                    if v in matrice[x-1][y-1]:
                        # Stop the loop when the number is already found
                        if len(matrice[x-1][y-1]) == 1:
                            cond = False

                        # First we met this number then record the coordinates
                        if found_row == 0:
                            col = x
                            row = y
                            found_row = 1
                            found_col = 1
                            debug('Spy 0', v, col, row, x, y)
                        else:
                            debug('Spy 0.5', v, col, row, x, y)
                            # Found a second occurence of the number
                            if col == x:
                                if found_row == 2:
                                    # Found a new occurence but not on the same row
                                    debug('Spy 6', v, col, row, x, y)
                                    found_row = 0
                                    found_col = 0
                                    cond = False
                                else:
                                    debug('Spy 1', v, col, row, x, y)
                                    found_col = 2
                            else:
                                if found_col == 2:
                                    # Found a new occurence but not on the same column
                                    debug('Spy 2', v, col, row, x, y)
                                    found_row = 0
                                    found_col = 0
                                    cond = False
                                else:
                                    if row == y:
                                        debug('Spy 3', v, col, row, x, y)
                                        found_row = 2
                                    else:
                                        if found_row == 2:
                                            # Found a new occurence but not on the same row
                                            debug('Spy 4', v, col, row, x, y)
                                            found_row = 0
                                            found_col = 0
                                            cond = False
                                        else:
                                            # Neither the column and the row are the same so stop
                                            found_row = 0
                                            found_col = 0
                                            cond = False

                    # Continue the reading
                    x += 1
                    if x > i * 3 + 3:
                        y += 1
                        x = i * 3 + 1
                        if y > j * 3 + 3:
                            # Stop the loop if not found
                            cond = False

                if found_row == 2:
                    print("Found {} that is only in row {} of block({},{})".format(v, row, i+1, j+1))
                    found_changes != RemoveNumberFromOtherBlocksRow(v, row, i+1, j+1)                    

                if found_col == 2:
                    print("Found {} that is only in col {} of block({},{})".format(v, col, i+1, j+1))
                    found_changes != RemoveNumberFromOtherBlocksCol(v, col, i+1, j+1)

                if found_row == 1 and found_col == 1:
                    if matrice_found[col-1][row-1] == 0:
                        print("Found {} that can be only in cell({},{})".format(v, col, row))
                        AddValueInMatrix(col, row, v)
                        #DisplayMatrix()

for line in open(fileName):
    line = line.strip()
    (x,y,v) = line.split(',')
    if not x.isdigit or not y.isdigit() or not v.isdigit():
        raise BaseException('X - {} or Y - {} or V - {} are not integers '.format(x, y, v))
    x = int(x)
    y = int(y)
    v = int(v)
    if x<1 or x>9 :
        raise BaseException("X value {} out of range (should be between 1 and 9)".format(x))
    if y<1 or y>9:
        raise BaseException("Y value {} out of range (should be between 1 and 9)".format(y))
    if v<1 or v>9:
        raise BaseException("V value {} out of range (should be between 1 and 9)".format(v))
    AddValueInMatrix(x, y, v)


DisplayMatrix()

loop = True
while loop:    
    LooksForUniqueColumnRow()

DisplayMatrix()
