#!python2
import os
import sys
import time
import random
import msvcrt#currently only works for windows os
import platform
import threading
from queue import Queue
clear = lambda: os.system("cls") if platform.system() == "Windows" else lambda: os.system("clear")
_domain = 10#12
_range = 18#23
mid = _domain / 2
simple = ((mid, _range),)
I = ((mid, _range), (mid, _range + 1), (mid, _range + 2))
i = ((mid, _range), (mid, _range + 1))
J = ((mid, _range), (mid + 1, _range), (mid + 1, _range + 1), (mid + 1, _range + 2))
L = ((mid, _range), (mid - 1, _range), (mid - 1, _range + 1), (mid - 1, _range + 2))
O = ((mid, _range), (mid, _range + 1), (mid + 1, _range), (mid + 1, _range + 1))
Z = ((mid, _range), (mid - 1, _range), (mid - 1, _range + 1), (mid - 2, _range + 1))
T = ((mid, _range), (mid + 1, _range), (mid + 1, _range - 1), (mid + 1, _range + 1))
S = ((mid, _range), (mid + 1, _range), (mid + 1, _range + 1), (mid + 2, _range + 1))
#The array in this program is a dictionary of tuple coordinate keys (x, y) that
#each correspond to a dictionary containing specific values
def create_grid(width, height, value):
    #creates the grid
    grid = {}
    for x in range(width):
        for y in range(height):
            grid[x, y] = value
    return grid
#
def add_edges(grid, value):
    #reproduces grid but with borders, except on the top
    #can be replaced If a list of edge points can be generated
    grid = grid.copy()
    width = 0
    for key in grid:
        width = key[0] + 1 if key[0] >= width else width
    height = len(grid) / width
    for x in range(width):
        for y in range(height):
            if x == 0 or x == width - 1 or y == 0:
                grid[x,y] = value
    return grid
#
def grid_add(grid, points, values):
    grid = grid.copy()
    x, y = 0, 1
    if len(points) != len(values):
        if len(values) == 1 or values == "":
            values = [values for coordinate in range(len(points))]
        else:
            print "invalid amount of values"
            sys.exit(0)
    #adds a list of values to a grid
    index = 0
    for coordinate in points:
        grid[coordinate] = values[index]
        index += 1
    return grid
#
def grid_render(grid, default = " ", buffer = 1):
    #returns a text representation of the grid based on the data inside it
    render = ""
    width = 0
    for key in grid:
        width = key[0] + 1 if key[0] >= width else width
    height = len(grid) / width
    '''adding key:value pairs to grid can cause len(grid) to increase and could result
    in unintended errors. fixing this issue can allow things to be added to the matrix
    in relative to the grid instead of within it'''
    text = ""
    for y in range(height - 1, -1, -1):
        for x in range(width):
            text += default + " " * buffer if grid[x,y] == "" else grid[x,y] + " " * buffer
        text += "\n"
    text = text[:len(text) - 1]
    #removes the last "\n" character from the render
    return text
#
def render_replace(render, points, values, buffer = 1):
    #returns a altered text representation by replacing values
    render = render.split("\n")
    offset = buffer + 1
    x = 0
    y = 1
    if len(points) != len(values):
        if len(values) == 1:
            values = [values for coordinate in range(len(points))]
        else:
            print "Amount of values provided is not acceptable"
            sys.exit(0)
    for coordinate in points:
        if coordinate[x] not in range(len(render[0]) / offset):
            print "An x coordinate is out of range"
            sys.exit(0)
        if coordinate[y] not in range(len(render)):
            print "A y coordinate is out of range"
            sys.exit(0)
    #
    value_index = 0
    for coordinate in points:
        invert_y = len(render) - coordinate[y] - 1
        row = render[invert_y]
        row = row[:coordinate[x] * offset] + values[value_index] + row[(coordinate[x] * offset) + 1:]
        render[invert_y] = row
        value_index += 1
    patch = ""
    for split in render:
        patch += split + "\n"
    patch = patch[:len(patch) - 1]
    #removes the last "\n" character from the patch
    render = patch
    return render
    #it'd be useful to create other operations such as moving point values to new points
    #instead of replacing the point values
#
def grid_collision(grid, points, direction, distance = 1):
    #determines if a space a block intends to enter is occupied
    x, y = 0, 1
    xdelta, ydelta = 0, 0
    #returns false if any of the points will collide with a point in grid that contains a value
    if direction not in ["90rotation", "-90rotation"]:
        if direction in ["left", "right"]:
            axis = x
            xdelta = -distance if direction == "left" else distance
            ydelta = 0
        elif direction in ["down", "up"]:
            axis = y
            ydelta = -distance if direction == "down" else distance
            xdelta = 0
        for coordinate in points:
            destination = (coordinate[x] + xdelta, coordinate[y] + ydelta)
            try:
                if grid[destination] != "":
                    return True
            except KeyError:
                if destination[x] not in range(1,_domain - 1):
                    return True
                pass
    elif direction == "-90rotation":
        origin = points[0]
        for coordinate in points[1:]:
            xdelta = -(coordinate[y] - origin[y]) - (coordinate[x] - origin[x])
            #print xdelta, raw_input()
            ydelta = (coordinate[x] - origin[x]) - (coordinate[y] - origin[y])
            #print ydelta, raw_input()
            destination = (coordinate[x] + xdelta, coordinate[y] + ydelta)
            try:
                if grid[destination] != "":
                    return True
            except KeyError:
                pass
    elif direction == "90rotation":
        origin = points[0]
        for coordinate in points[1:]:
            xdelta = (coordinate[y] - origin[y]) - (coordinate[x] - origin[x])
            #print xdelta, raw_input()
            ydelta = -(coordinate[x] - origin[x]) - (coordinate[y] - origin[y])
            #print ydelta, raw_input()
            destination = (coordinate[x] + xdelta, coordinate[y] + ydelta)
            try:
                if grid[destination] != "":
                    return True
            except KeyError:
                pass
    return False
    #This function can be replaced with a function that just checks a list of points for values, This would prevent the same calculation from being repeated
#
def main():
    highscore = ""
    with open("highscore.txt", "a+") as file:
        scan = file.read()
        if scan != "":
            highscore = "\n" + scan
    #runs the code
    score = 0
    x, y = 0, 1
    width = _domain
    height = _range
    empty = " "
    #domain and range are global for now
    matrix = create_grid(width, height, "")
    matrix = add_edges(matrix, "#")
    output = grid_render(matrix, empty)
    drop_point = (mid, height)
    blocks = (simple, i, I, I, J, L, O, Z, T, T, S)
    #1st coordinate in blocks must be equal to drop_point
    focus = list(random.choice(blocks))
    next = list(random.choice(blocks))
    simulation = "on"
    imprint = None
    frameclock = {0}
    drop_rate = 0.5
    #
    while simulation != "off":
        start = time.time()
        #
        if grid_collision(matrix, focus, "down", 1) == False:
            old_points = []
            new_points = []
            for coordinate in focus:
                if coordinate[y] in range(height):
                    old_points.append(coordinate)
            temp_focus = []
            for coordinate in focus:
                temp_focus.append((coordinate[x], coordinate[y] - 1))
            focus = temp_focus
            for coordinate in focus:
                if coordinate[y] in range(height):
                    new_points.append(coordinate)
            if old_points != [] or new_points != []:
                output = render_replace(output, old_points, empty)
                output = render_replace(output, new_points, "x")
        else:        
            if grid_collision(matrix, [drop_point], "down", 1) == False:
                matrix = grid_add(matrix, focus, "x")
                focus = next
                next = list(random.choice(blocks))
            else:
                time.sleep(1.5)
                clear()
                print "game over\n" + highscore + "\nyour score: " + str(score)
                if highscore == "":
                    print "you created a highscore!"
                    if raw_input("enter 'yes' if you you like to save your score: ") in ["yes", "y"]:
                        name = raw_input("name?: ")
                        with open("highscore.txt", "w+") as file:
                            file.write(name + ": " + str(score))
                elif int(filter(str.isdigit, highscore)) < score:
                    print "congratulations: you beat the highscore!"
                    if raw_input("enter 'yes' if you you like to save your score: ") in ["yes", "y"]:
                        name = raw_input("name?: ")
                        try:
                            file = open("highscore.txt", "w")
                            file.write(name + ": " + str(score))
                        finally:
                            file.close()
                simulation = "off"
                #print max(frameclock)
                choice = raw_input("play again?: ")
                if choice == '':
                    pass
                elif choice[0].lower() == "y":
                    main()
            filled = 0
            high_row = 0
            #removing filled rows
            #adjusts for borders
            for y_val in range(1, height - 1):
                fill = []
                for x_val in range(1, width - 1):
                    if matrix[x_val,y_val] != "":
                        fill.append((x_val,y_val))
                    if len(fill) == width - 2:
                        for coordinate in fill:
                            matrix[coordinate] = ""
                        output = render_replace(output, fill, empty)
                        filled += 1
                        high_row = y_val
            score += 5 ** filled if filled > 0 else 0
            #shifting rows down
            #adjusts for borders
            if filled > 0:
                clear()
                print output + highscore + "\ncurrent score: " + str(score) + "\nnext: # of blocks = " + str(len(next))
                for y_val in range(1 + high_row, height):
                    falling_blocks = []
                    for x_val in range(1, width - 1):
                        if matrix[x_val,y_val] != "":
                            falling_blocks.append((x_val,y_val))
                    if falling_blocks != []:
                        felled_blocks = falling_blocks[:]
                        while grid_collision(matrix, felled_blocks, "down", 1) != True:
                            temp = felled_blocks[:]
                            felled_blocks = []
                            for coordinate in temp:
                                felled_blocks.append((coordinate[x], coordinate[y] - 1))
                        matrix = grid_add(matrix, falling_blocks, "")
                        matrix = grid_add(matrix, felled_blocks, "x")
                        output = render_replace(output, falling_blocks, " ")
                        output = render_replace(output, felled_blocks, "x")
                        clear()
                        print output + highscore + "\ncurrent score: " + str(score) + "\nnext: # of blocks = " + str(len(next))
                        time.sleep(0.15)
            continue
        if output != imprint:
            #raw_input()
            clear()
            print output + highscore + "\ncurrent score: " + str(score) + "\nnext: # of blocks = " + str(len(next))
            imprint = output
        frameclock.add(time.time() - start)
        #print .3 - (time.time() - start), raw_input()
        moved = False
        #while time.time() - start < .19:
        #   pass
        while time.time() - start < drop_rate:
            start2 = time.time()
            if msvcrt.kbhit():
                move = msvcrt.getch()
                if move == "a":
                    if grid_collision(matrix, focus, "left", 1) == False:
                        old_points = []
                        new_points = []
                        for coordinate in focus:
                            if coordinate[y] in range(height):
                                old_points.append(coordinate)
                        temp_focus = []
                        for coordinate in focus:
                            temp_focus.append((coordinate[x] - 1, coordinate[y]))
                        focus = temp_focus
                        for coordinate in focus:
                            if coordinate[y] in range(height):
                                new_points.append(coordinate)
                        if old_points != [] or new_points != []:
                            output = render_replace(output, old_points, empty)
                            output = render_replace(output, new_points, "x")
                elif move == "d":
                    if grid_collision(matrix, focus, "right", 1) == False:
                        old_points = []
                        new_points = []
                        for coordinate in focus:
                            if coordinate[y] in range(height):
                                old_points.append(coordinate)
                        temp_focus = []
                        for coordinate in focus:
                            temp_focus.append((coordinate[x] + 1, coordinate[y]))
                        focus = temp_focus
                        for coordinate in focus:
                            if coordinate[y] in range(height):
                                new_points.append(coordinate)
                        if old_points != [] or new_points != []:
                            output = render_replace(output, old_points, empty)
                            output = render_replace(output, new_points, "x")
                elif move == "s":
                    if grid_collision(matrix, focus, "down", 1) == False:
                        old_points = []
                        new_points = []
                        for coordinate in focus:
                            if coordinate[y] in range(height):
                                old_points.append(coordinate)
                        temp_focus = []
                        for coordinate in focus:
                            temp_focus.append((coordinate[x], coordinate[y] - 1))
                        focus = temp_focus
                        for coordinate in focus:
                            if coordinate[y] in range(height):
                                new_points.append(coordinate)
                        if old_points != [] or new_points != []:
                            output = render_replace(output, old_points, empty)
                            output = render_replace(output, new_points, "x")
                elif move == "q":
                    if grid_collision(matrix, focus, "-90rotation") == False:
                        old_points = []
                        new_points = []
                        for coordinate in focus:
                            if coordinate[y] in range(height):
                                old_points.append(coordinate)
                        temp_focus = []
                        for coordinate in focus:
                            origin = focus[0]
                            xdelta = -(coordinate[y] - origin[y]) - (coordinate[x] - origin[x])
                            ydelta = (coordinate[x] - origin[x]) - (coordinate[y] - origin[y])
                            destination = (coordinate[x] + xdelta, coordinate[y] + ydelta)
                            temp_focus.append(destination)
                        focus = temp_focus
                        for coordinate in focus:
                            if coordinate[y] in range(height):
                                new_points.append(coordinate)
                        if old_points != [] or new_points != []:
                            output = render_replace(output, old_points, empty)
                            output = render_replace(output, new_points, "x")
                elif move == "e":
                    if grid_collision(matrix, focus, "90rotation") == False:
                        old_points = []
                        new_points = []
                        for coordinate in focus:
                            if coordinate[y] in range(height):
                                old_points.append(coordinate)
                        temp_focus = []
                        for coordinate in focus:
                            origin = focus[0]
                            xdelta = (coordinate[y] - origin[y]) - (coordinate[x] - origin[x])
                            ydelta = -(coordinate[x] - origin[x]) - (coordinate[y] - origin[y])
                            destination = (coordinate[x] + xdelta, coordinate[y] + ydelta)
                            temp_focus.append(destination)
                        focus = temp_focus
                        for coordinate in focus:
                            if coordinate[y] in range(height):
                                new_points.append(coordinate)
                        if old_points != [] or new_points != []:
                            output = render_replace(output, old_points, empty)
                            output = render_replace(output, new_points, "x")
                #time.sleep(.03)
            if output != imprint:
                clear()
                print output + highscore + "\ncurrent score: " + str(score) + "\nnext: # of blocks = " + str(len(next))
                imprint = output
            if drop_rate > .30:
                drop_rate -= 0.0000009
            #print drop_rate
        
#
if __name__ == "__main__":
    main()
