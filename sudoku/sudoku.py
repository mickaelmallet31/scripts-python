#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import json
import Tkinter as tk

MAX_COL = 9
MAX_ROW = 9

matrice = [[[1,2,3,4,5,6,7,8,9] for x in range(MAX_COL)] for y in range(MAX_ROW)]
matrice_found = [[0 for x in range(MAX_COL)] for y in range(MAX_ROW)]

fileName ="grille.json"

class SudokuGrill(tk.Frame):
    def __init__(self, parent, rows=MAX_ROW, columns=MAX_COL, size=32, color1="white", color_text_orig="black", color_text_found="darkblue"):
        '''size is the size of a square, in pixels'''

        self.rows = rows
        self.columns = columns
        self.size = size
        self.color1 = color1
        self.color_text_orig = color_text_orig
        self.color_text_found = color_text_found
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
        color = self.color_text_found
        if matrice_found[column-1][row-1] == 2:
            color = self.color_text_orig
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

def DisplayMatrix(only_given_values=False):
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

    # Display the grid with tkinter module
    root = tk.Tk()
    board = SudokuGrill(root)
    board.pack(side="top", fill="both", expand="true", padx=4, pady=4)
    for j in range(1, MAX_COL+1):
        for i in range(1, MAX_ROW+1):
            if only_given_values:
                if matrice_found[i-1][j-1] == 2:
                    board.addpiece('text{}{}'.format(i,j), matrice[i-1][j-1], j, i)
            else:
                board.addpiece('text{}{}'.format(i,j), matrice[i-1][j-1], j, i)
    root.mainloop()

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
                    print("Found {} that can be only in cell({},{})".format(value, i, j))
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
                    print("Found {} that can be only in cell({},{})".format(value, i, j))
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
                    found_changes != RemoveNumberFromOtherBlocksRow(v, row, i+1, j+1)                    

                if found_col == 2:
                    print("Found {} that is only in col {} of block({},{})".format(v, col, i+1, j+1))
                    found_changes != RemoveNumberFromOtherBlocksCol(v, col, i+1, j+1)

                if found_row == 1 and found_col == 1:
                    if matrice_found[col-1][row-1] == 0:
                        print("Found {} that can be only in cell({},{})".format(v, col, row))
                        AddValueInMatrix(col, row, v)
                        #DisplayMatrix()

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
                    AddValueInMatrix(x, y, v)
                    matrice_found[x-1][y-1] = 2
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
            AddValueInMatrix(x, y, v)
            matrice_found[x-1][y-1] = 2


    DisplayMatrix(only_given_values=True)

    loop = True
    while loop:
        LooksForUniqueColumnRow()

    DisplayMatrix()
