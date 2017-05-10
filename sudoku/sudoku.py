#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import json
import sys
from copy import deepcopy

try:
    # for Python2
    import Tkinter as tk
except ImportError:
    # for Python3
    import tkinter as tk

class Matrix_Corruption(Exception):
    pass

COLOR_EMPTY = 0
COLOR_FOUND = 1
COLOR_CHOSEN = 3
COLOR_PROVIDED = 2

MAX_COL = 9
MAX_ROW = 9

matrice = [[[1,2,3,4,5,6,7,8,9] for x in range(MAX_COL)] for y in range(MAX_ROW)]
matrice_found = [[COLOR_EMPTY for x in range(MAX_COL)] for y in range(MAX_ROW)]
error_code = 0

fileName = "grille.json"
if len(sys.argv) > 1:
    fileName = sys.argv[1]

class SudokuGrill(tk.Frame):
    def __init__(self, parent, rows=MAX_ROW, columns=MAX_COL, size=50, color1="white"):
        '''size is the size of a square, in pixels'''

        self.rows = rows
        self.columns = columns
        self.size = size
        self.color1 = color1
        self.pieces = {}

        canvas_width = columns * size
        canvas_height = rows * size

        tk.Frame.__init__(self, parent)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0,
                                width=canvas_width, height=canvas_height, background="bisque")
        self.canvas.pack(side="top", fill="both", expand=True, padx=2, pady=2)

        # this binding will cause a refresh if the user interactively
        # changes the window size
        self.canvas.bind("<Configure>", self.refresh)

    def addpiece(self, name, text, row=1, column=1):
        '''Add a piece to the playing board'''
        color = "blue"
        if matrice_found[column-1][row-1] == COLOR_PROVIDED:
            color = "black"
        elif matrice_found[column-1][row-1] == COLOR_CHOSEN:
            color = "red"
            
        self.canvas.create_text(0,0, tags=(name, "number"), fill=color, font="Times 20 italic bold",
                        text=text)
        self.placepiece(name, row-1, column-1)

    def placepiece(self, name, row, column):
        '''Place a piece at the given row/column'''
        self.pieces[name] = (row, column)
        x0 = (column * self.size) + int(self.size/2)
        y0 = (row * self.size) + int(self.size/2)
        self.canvas.coords(name, x0, y0)

    def refresh(self, event):
        '''Redraw the board, possibly in response to window being resized'''
        xsize = int((event.width-1) / self.columns)
        ysize = int((event.height-1) / self.rows)
        self.size = min(xsize, ysize)
        self.canvas.delete("square")
        color = self.color1
        # Draw the 9x9 grill
        for row in range(self.rows):
            for col in range(self.columns):
                x1 = (col * self.size)
                y1 = (row * self.size)
                x2 = x1 + self.size
                y2 = y1 + self.size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=color, tags="square")
        # Draw the 3x3 blocks grill
        for row in range(3):
            for col in range(3):
                x1 = (col * self.size * 3)
                y1 = (row * self.size * 3)
                x2 = x1 + self.size * 3
                y2 = y1 + self.size * 3
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", width=3, tags="square")
        for name in self.pieces:
            self.placepiece(name, self.pieces[name][0], self.pieces[name][1])
        self.canvas.tag_raise("piece")
        self.canvas.tag_lower("square")


def debug(*list):
    #print(list)
    pass

def ErrorMgt(msg):
    """ Manage the error code
    """
    print msg
    #print sys.exc_info()
    raise Matrix_Corruption
    
def DisplayMatrix(selected_color):
    if 0:
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
    else:
        # Display the grid with tkinter module
        root = tk.Tk()
        root.wm_title(fileName)
        board = SudokuGrill(root)
        board.pack(side="top", fill="both", expand="true", padx=4, pady=4)
        for j in range(1, MAX_COL+1):
            for i in range(1, MAX_ROW+1):
                if selected_color:
                    if matrice_found[i-1][j-1] == selected_color:
                        board.addpiece('text{}{}'.format(i,j), matrice[i-1][j-1], j, i)
                else:
                    board.addpiece('text{}{}'.format(i,j), matrice[i-1][j-1], j, i)
        root.bind("<Return>", lambda e: root.destroy())
        root.mainloop()

def AddValueInMatrix(x, y, v, filter=COLOR_FOUND):
    global loop

    debug("AddValueInMatrix: v={} in ({},{})".format(v, x, y))
    # Remove the value in the col
    for i in range(1, MAX_COL+1):
        if i != x:
            if v in matrice[i-1][y-1]:
                if len(matrice[i-1][y-1]) == 1:
                    ErrorMgt('Error when removing {} from column {} in ({},{})'.format(v, x, i, y))
                else:
                    matrice[i-1][y-1].remove(v)
                    if len(matrice[i-1][y-1]) == 1:
                        value = matrice[i-1][y-1][0]
                        print("Cell({},{}) : only {} can be there".format(i, y, value))
                        AddValueInMatrix(i, y, value)

    # Remove the value in the row
    for j in range(1, MAX_ROW+1):
        if j != y:
            if v in matrice[x-1][j-1]:
                if len(matrice[x-1][j-1]) == 0:
                    ErrorMgt('Error when removing {} from row {} in ({},{})'.format(v, y, x, j))
                else:
                    matrice[x-1][j-1].remove(v)
                    if len(matrice[x-1][j-1]) == 1:
                        value = matrice[x-1][j-1][0]
                        print("Cell({},{}) : only {} can be there".format(x, j, value))
                        AddValueInMatrix(x, j, value)

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
                    ErrorMgt('Error when removing {} in ({},{})'.format(v, i, j))
                else:
                    if len(matrice[i-1][j-1]) == 1:
                        value = matrice[i-1][j-1][0]
                        print("Cell({},{}): only {} can be there".format(value, i, j))
                        AddValueInMatrix(i, j, value)

    matrice[x-1][y-1] = [v]
    if matrice_found[x-1][y-1] == COLOR_EMPTY:
        matrice_found[x-1][y-1] = filter
    loop = True

def RemoveNumberFromOtherBlocksCol(v, col, x, y):
    global loop
    error_code = False
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

def RemoveNumberFromOtherBlocksRow(v, row, x, y):
    global loop
    removed = False
    
    for i in range(1, 9+1):
        if i >= (x * 3 - 2) and i <= (x * 3):
            continue
        if v in matrice[i-1][row-1]:
            matrice[i-1][row-1].remove(v)
            if len(matrice[i-1][row-1]) == 1:
                ErrorMgt("Found new value {} alone in {},{}".format(matrice[i-1][row-1][0], i, row))
                AddValueInMatrix(i, row, matrice[i-1][row-1][0])
            removed = True

    if removed == True:
        #DisplayMatrix()
        loop = True

def checkResolvedGrid():
    """ Check that the current grid is resolved by looking for any cell with
    more than one number. In this case the function will return FALSE. Otherwise
     if at the end of the loop it will return TRUE
    """
    for i in range(1, 9+1):
        for j in range(1, 9+1):
            if len(matrice[i-1][j-1]) > 1:
                return False

    return True

def LooksForUniqueColumnRow():
    """
    """
    global loop

    for i in range(1, MAX_COL+1):
        for j in range(1, MAX_ROW+1):
            # Skip the cell if there is only one value
            if len(matrice[i-1][j-1]) == 1:
                continue

            # For each value of a specific cell
            for value in matrice[i-1][j-1]:

                # Check that this value is elsewhere in the same row
                found = False
                for i2 in range(1, MAX_COL+1):
                    if i2 != i and value in matrice[i2-1][j-1]:
                        found = True
                        break
                if found == False:
                    # This value could be only in this cell
                    print("Cell({},{}) : only {} can be there".format(i, j, value))
                    AddValueInMatrix(i, j, value)

                # Skip the cell if there is only one value
                if len(matrice[i-1][j-1]) == 1:
                    continue

                # Check that this value is elsewhere in the same column
                found = False
                for j2 in range(1, MAX_ROW+1):
                    if j2 != j and value in matrice[i-1][j2-1]:
                        found = True
                        break
                if found == False:
                    # This value could be only in this cell
                    print("Cell({},{}) : only {} can be there".format(i, j, value))
                    AddValueInMatrix(i, j, value)

                # Check if this value is elsewhere in the same block

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
                    RemoveNumberFromOtherBlocksRow(v, row, i+1, j+1)

                if found_col == 2:
                    print("Found {} that is only in col {} of block({},{})".format(v, col, i+1, j+1))
                    RemoveNumberFromOtherBlocksCol(v, col, i+1, j+1)

                if found_row == 1 and found_col == 1:
                    if matrice_found[col-1][row-1] == COLOR_EMPTY:
                        print("Cell({},{}) : only {} can be there".format(col, row, v))
                        matrice_found[col-1][row-1] = COLOR_FOUND
                        AddValueInMatrix(col, row, v)

#
# Main function
#
if __name__ == "__main__":
    if re.search('.json', fileName):
        data_json = json.load(open(fileName))
        y = 0
        for data in data_json:
            x = 0
            y += 1
            for v in data:
                x += 1
                if v:
                    matrice_found[x-1][y-1] = COLOR_PROVIDED
                    AddValueInMatrix(x, y, v)
    else:
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
            matrice_found[x-1][y-1] = COLOR_PROVIDED
            AddValueInMatrix(x, y, v)


    DisplayMatrix(COLOR_PROVIDED)

    loop = True
    retry = True
    retry_i = 1
    retry_j = 1
    retry_index = 0
    backup_matrice = []
    while retry:
        while loop:
            LooksForUniqueColumnRow()
            if loop == False:
                retry = (checkResolvedGrid() == False)

        if retry:

            tried_this_value = False
            change_value = False
            while (retry_i <= 9) and tried_this_value == False:

                while (retry_j <= 9) and tried_this_value == False and change_value == False:
                
                    if len(matrice[retry_i-1][retry_j-1]) == 2:
                        
                        while (retry_index < 2) and tried_this_value == False:

                            debug('try the value {} of index {} at the cell ({}, {})'.format(matrice[retry_i-1][retry_j-1][retry_index], retry_index, retry_i, retry_j))
    
                            try:
                                tried_this_value = True
                                backup_matrice = deepcopy(matrice)
                                AddValueInMatrix(retry_i, retry_j, matrice[retry_i-1][retry_j-1][retry_index])
                                matrice_found[retry_i-1][retry_j-1] = COLOR_CHOSEN
                            except Matrix_Corruption:
                                matrice = deepcopy(backup_matrice)
                                loop = False
                                change_value = True
                                tried_this_value = False
                                pass

                            if change_value == True:
                                retry_index += 1
                                change_value = False
                                if retry_index >= 2:
                                    retry_index = 0
                                    change_value = True                                    
                    else:
                        change_value = True
                                
                    if change_value == True:
                        retry_j += 1
                        change_value = False
                        if retry_j > 9:
                            retry_j = 1
                            change_value = True
                        
                if change_value == True:
                    retry_i += 1
                    change_value = False

    DisplayMatrix(COLOR_EMPTY)
