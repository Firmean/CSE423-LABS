from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import numpy as np
import time
import math

width = 800
height = 700

board_points = np.array([[int(width * 0.15)], [10], [1]])
radius = 5
startGame = False
circle_points = np.array([[board_points[0][0] + 45], [board_points[1][0] + radius], [1]])

translateVector = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
translateBoardLeft = np.array([[1, 0, -8], [0, 1, 0], [0, 0, 1]]) #reflection  matrix
translateBoardRight = np.array([[1, 0, 8], [0, 1, 0], [0, 0, 1]])
reflect_x = np.array([[1, 0, 0], [0, -1, 0], [0, 0, 1]])
reflect_y = np.array([[-1, 0, 0], [0, 1, 0], [0, 0, 1]])
board_width = 90

blocks = {}
block_width = 50
block_height = 15
paused = False


pauseScale = np.array([[2, 0, 0], [0, 2, 0], [0, 0, 1]])
pauseBoxLeftUpCoord = np.array([[-5], [1], [1]])
pauseBoxRightUpCoord = np.array([[5], [1], [1]])
pauseBoxRightDownCoord = np.array([[5], [-1], [1]])
pauseBoxLeftDownCoord = np.array([[-5], [-1], [1]])
pauseBoxCoords = [pauseBoxLeftUpCoord, pauseBoxRightUpCoord, pauseBoxRightDownCoord, pauseBoxLeftDownCoord]
translatePauseCoords = np.array([[1, 0, width // 2], [0, 1, height // 2], [0, 0, 1]])

timesScaled = 5 #initialising the conditions.
reversed = True
score = 0
blockPoint = 10
scoreHeight = 20
scoreWidth = 10
num_coords = (10, height - 10)
gameOver = False
gameOverBoxCoords = [((0 + width) // 10, (height * 6) // 10),
                     (width - (0 + width) // 10, (height * 6) // 10),
                     (width - (0 + width) // 10, (height * 4) // 10),
                     ((0 + width) // 10, (height * 4) // 10)
                     ]

level = 1
num_blocks = 10
level_points = (width - 10, height - 10)


def draw_points(x, y):
    glPointSize(3)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()


def iterate():
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, width, 0.0, height, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def zone0to1(x, y):
    return y, x


def zone1to0(x, y):
    return y, x


def zone0to2(x, y):
    return -y, x


def zone2to0(x, y):
    return y, -x


def zone0to3(x, y):
    return -x, y


def zone3to0(x, y):
    return -x, y


def zone0to4(x, y):
    return -x, -y


def zone4to0(x, y):
    return -x, -y


def zone0to5(x, y):
    return -y, -x


def zone5to0(x, y):
    return -y, -x


def zone0to6(x, y):
    return y, -x


def zone6to0(x, y):
    return -y, x


def zone0to7(x, y):
    return x, -y


def zone7to0(x, y):
    return x, -y


def zone0(x, y):
    return x, y


def findZone(a, b):
    dy = b[1] - a[1]
    dx = b[0] - a[0]

    if dx >= 0:
        if dy >= 0:
            if abs(dx) >= abs(dy):
                return 0
            else:
                return 1
        else:
            if abs(dx) >= abs(dy):
                return 7
            else:
                return 6
    else:
        if dy >= 0:
            if abs(dx) >= abs(dy):
                return 3
            else:
                return 2
        else:
            if abs(dx) >= abs(dy):
                return 4
            else:
                return 5


def zone1to0(x, y):
    return y, x


def zone1to2(x, y):
    return -x, y


def zone1to3(x, y):
    return -y, x


def zone1to4(x, y):
    return -y, -x


def zone1to5(x, y):
    return -x, -y


def zone1to6(x, y):
    return x, -y


def zone1to7(x, y):
    return y, -x


def draw_circle_in_zone1(r):
    x = 0
    y = r
    d_init = 1 - r
    points = []
    while (x < y):
        if (d_init >= 0):
            d_init = d_init + 2 * x - 2 * y + 5
            y = y - 1
        else:
            d_init = d_init + 2 * x + 3

        points.append((x, y))
        x = x + 1

    return points


def draw_circle(r):
    values = draw_circle_in_zone1(r)
    all_points = values.copy()
    for value in values:
        all_points.append((zone1to0(value[0], value[1])))
        all_points.append((zone1to2(value[0], value[1])))
        all_points.append((zone1to3(value[0], value[1])))
        all_points.append((zone1to4(value[0], value[1])))
        all_points.append((zone1to5(value[0], value[1])))
        all_points.append((zone1to6(value[0], value[1])))
        all_points.append((zone1to7(value[0], value[1])))

    return all_points


def drawLine(x1, y1, x2, y2):
    if y2 < y1:
        x1, y1, x2, y2 = x2, y2, x1, y1
    zone_return = {0: zone0, 1: zone1to0, 2: zone2to0, 3: zone3to0, 4: zone4to0, 5: zone5to0, 6: zone6to0, 7: zone7to0}
    zone_transfer = {0: zone0, 1: zone0to1, 2: zone0to2, 3: zone0to3, 4: zone0to4, 5: zone0to5, 6: zone0to6,
                     7: zone0to7}
    zone = findZone((x1, y1), (x2, y2))
    new_coords = [zone_transfer[zone](x1, y1), zone_transfer[zone](x2, y2)]
    x1, y1 = new_coords[0]
    x2, y2 = new_coords[1]
    dy = y2 - y1
    dx = x2 - x1
    d_init = 2 * dy - dx
    d_ne = 2 * dy - 2 * dx
    d_e = 2 * dy
    while (x1 != x2 or y1 != y2):
        points = zone_return[zone](x1, y1)
        draw_points(points[0], points[1])
        if (d_init > 0):
            d_init = d_init + d_ne
            y1 = y1 + 1
        else:
            d_init = d_init + d_e

        x1 = x1 + 1

    points = zone_return[zone](x2, y2)
    draw_points(points[0], points[1])



def drawP(x, y):
    drawLine(x, y, x, y - 50)
    drawLine(x, y, x + 30, y)
    drawLine(x + 30, y, x + 30, y - 25)
    drawLine(x + 30, y - 25, x, y - 25)


def drawA(x, y):
    drawLine(x, y, x, y - 50)
    drawLine(x, y, x + 30, y)
    drawLine(x + 30, y, x + 30, y - 50)
    drawLine(x, y - 25, x + 30, y - 25)


def drawU(x, y):
    drawLine(x, y, x, y - 50)
    drawLine(x + 30, y, x + 30, y - 50)
    drawLine(x, y - 50, x + 30, y - 50)


def drawS(x, y):
    drawLine(x, y, x + 30, y)
    drawLine(x + 30, y, x + 30, y - 15)
    drawLine(x, y, x, y - 25)
    drawLine(x, y - 25, x + 30, y - 25)
    drawLine(x + 30, y - 25, x + 30, y - 50)
    drawLine(x + 30, y - 50, x, y - 50)
    drawLine(x, y - 50, x, y - 35)


def drawE(x, y):
    drawLine(x, y, x, y - 50)
    drawLine(x, y, x + 30, y)
    drawLine(x, y - 25, x + 30, y - 25)
    drawLine(x, y - 50, x + 30, y - 50)


def drawD(x, y):
    drawLine(x, y, x, y - 50)
    drawLine(x, y, x + 20, y)
    drawLine(x + 20, y, x + 30, y - 10)
    drawLine(x + 30, y - 10, x + 30, y - 40)
    drawLine(x + 30, y - 40, x + 20, y - 50)
    drawLine(x + 20, y - 50, x, y - 50)


def draw_zero(x, y, scoreWidth=scoreWidth, scoreHeight=scoreHeight):
    drawLine(x, y, x + scoreWidth, y)
    drawLine(x + scoreWidth, y, x + scoreWidth, y - scoreHeight)
    drawLine(x + scoreWidth, y - scoreHeight, x, y - scoreHeight)
    drawLine(x, y - scoreHeight, x, y)


def draw_one(x, y, scoreHeight=scoreHeight):
    drawLine(x, y, x, y - scoreHeight)


def draw_two(x, y, scoreWidth=scoreWidth, scoreHeight=scoreHeight):
    drawLine(x, y, x + scoreWidth, y)
    drawLine(x + scoreWidth, y, x + scoreWidth, y - (scoreHeight // 2))
    drawLine(x + scoreWidth, y - (scoreHeight // 2), x, y - (scoreHeight // 2))
    drawLine(x, y - (scoreHeight // 2), x, y - scoreHeight)
    drawLine(x, y - scoreHeight, x + scoreWidth, y - scoreHeight)


def draw_three(x, y, scoreWidth=scoreWidth, scoreHeight=scoreHeight):
    drawLine(x + scoreWidth, y, x + scoreWidth, y - scoreHeight)
    drawLine(x, y, x + scoreWidth, y)
    drawLine(x, y - (scoreHeight // 2), x + scoreWidth, y - (scoreHeight // 2))
    drawLine(x, y - scoreHeight, x + scoreWidth, y - scoreHeight)


def draw_four(x, y, scoreWidth=scoreWidth, scoreHeight=scoreHeight):
    drawLine(x, y, x, y - (scoreHeight // 2))
    drawLine(x, y - (scoreHeight // 2), x + scoreWidth, y - (scoreHeight // 2))
    drawLine(x + scoreWidth, y, x + scoreWidth, y - scoreHeight)


def draw_five(x, y, scoreWidth=scoreWidth, scoreHeight=scoreHeight):
    drawLine(x, y, x + scoreWidth, y)
    drawLine(x, y, x, y - (scoreHeight // 2))
    drawLine(x + scoreWidth, y - (scoreHeight // 2), x, y - (scoreHeight // 2))
    drawLine(x + scoreWidth, y - (scoreHeight // 2), x + scoreWidth, y - scoreHeight)
    drawLine(x, y - scoreHeight, x + scoreWidth, y - scoreHeight)


def draw_six(x, y, scoreWidth=scoreWidth, scoreHeight=scoreHeight):
    drawLine(x, y, x + scoreWidth, y)
    drawLine(x, y, x, y - scoreHeight)
    drawLine(x + scoreWidth, y - (scoreHeight // 2), x, y - (scoreHeight // 2))
    drawLine(x + scoreWidth, y - (scoreHeight // 2), x + scoreWidth, y - scoreHeight)
    drawLine(x, y - scoreHeight, x + scoreWidth, y - scoreHeight)


def draw_seven(x, y, scoreWidth=scoreWidth, scoreHeight=scoreHeight):
    drawLine(x + scoreWidth, y, x + scoreWidth, y - scoreHeight)
    drawLine(x, y, x + scoreWidth, y)


def draw_eight(x, y, scoreWidth=scoreWidth, scoreHeight=scoreHeight):
    drawLine(x + scoreWidth, y, x + scoreWidth, y - scoreHeight)
    drawLine(x, y, x + scoreWidth, y)
    drawLine(x, y - (scoreHeight // 2), x + scoreWidth, y - (scoreHeight // 2))
    drawLine(x, y - scoreHeight, x + scoreWidth, y - scoreHeight)
    drawLine(x, y, x, y - scoreHeight)


def draw_nine(x, y, scoreWidth=scoreWidth, scoreHeight=scoreHeight):
    drawLine(x + scoreWidth, y, x + scoreWidth, y - scoreHeight)
    drawLine(x, y, x + scoreWidth, y)
    drawLine(x, y - (scoreHeight // 2), x + scoreWidth, y - (scoreHeight // 2))
    drawLine(x, y - scoreHeight, x + scoreWidth, y - scoreHeight)
    drawLine(x, y, x, y - (scoreHeight // 2))


def buttons(key, x, y):
    global window, startGame, paused, pauseBoxCoords, timesScaled, radius, startGame, circle_points, board_points, gameOver, score, translateVector, blocks, level
    if key == b'x':
        glutDestroyWindow(window)
    else:
        if key == b's' and startGame == False:
            startGame = True
            translateVector[0][2] = 2 #x coordinates of  2D matrix.
            translateVector[1][2] = 1 #y coordinate of 2D matrix.
        if key == b'p':
            paused = not paused
            pauseBoxLeftUpCoord = np.array([[-5], [1], [1]]) #creating pause box boundary
            pauseBoxRightUpCoord = np.array([[5], [1], [1]])
            pauseBoxRightDownCoord = np.array([[5], [-1], [1]])
            pauseBoxLeftDownCoord = np.array([[-5], [-1], [1]])
            timesScaled = 5
            pauseBoxCoords = [pauseBoxLeftUpCoord, pauseBoxRightUpCoord, pauseBoxRightDownCoord, pauseBoxLeftDownCoord]
        if key == b'n' and (gameOver == True or paused == True):
            board_points = np.array([[int(width * 0.15)], [10], [1]]) #restarting the whole game.
            radius = 5
            startGame = False
            circle_points = np.array([[board_points[0][0] + 60], [board_points[1][0] + radius], [1]])
            gameOver = False
            paused = False
            score = 0
            level = 1
            translateVector = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
            blocks = {}
            generate_blocks(num_blocks)


def keys(key, x, y):
    global startGame, board_points, circle_points, board_width
    if (paused == False and gameOver == False):
        if (key == GLUT_KEY_LEFT) and (board_points[0][0] > 0): #moving left and right with keys.
            board_points = np.matmul(translateBoardLeft, board_points)
        elif key == GLUT_KEY_RIGHT and (board_points[0][0] + board_width < width):
            board_points = np.matmul(translateBoardRight, board_points)

        if (startGame == False):
            circle_points = np.array([[board_points[0][0] + 60], [board_points[1][0] + radius], [1]])

    glutPostRedisplay()


def blockScreen():
    global blocks
    for tileList in blocks: #blocks is a dictionary.
        for tile in blocks[tileList]:
            i = 0
            while (i < block_height): #using the drawline function that generate the direction on which direction the ball will move.
                drawLine(tileList * block_width, tile * block_height + i, (tileList + 1) * block_width,
                         tile * block_height + i)
                i += 5


def updateScreen():
    global circle_points, board_width, blocks, timesScaled, reversed, score, blockPoint, num_coords, gameOver, num_blocks, radius, translateVector, board_points, startGame, level
    time.sleep(0.001) #using a delay.
    if (circle_points[1][0] + radius // 2 <= 0):  #if the ball hits the lower boundary.
        gameOver = True

    if (gameOver == True):#if the ball touches the lower boundary.
        for i in range(len(gameOverBoxCoords)):
            glColor3f(0.65, 0.0, 0.0)
            drawLine(gameOverBoxCoords[i][0], gameOverBoxCoords[i][1],
                     gameOverBoxCoords[(i + 1) % len(gameOverBoxCoords)][0],   #creating "game over" box.
                     gameOverBoxCoords[(i + 1) % len(gameOverBoxCoords)][1])

        final_score = str(score) #creating the final score that will come in the end. Score was an integer initially so converting it into string.
        total_width = 0

        for num in final_score:
            if num != "1": #if the score is not 1 .
                total_width += 50 #increasing the total width by 50
            else:
                total_width += 10 #or else increaing by 10.
        total_width -= 10
        score_coords = [gameOverBoxCoords[0][0] + (gameOverBoxCoords[1][0] - gameOverBoxCoords[0][0] - total_width) // 2, gameOverBoxCoords[0][1] - 25] #score that will come in the final box.
        # creating a numbers dictionary that have a key and a value.
        numbers = {"0": draw_zero, "1": draw_one, "2": draw_two, "3": draw_three, "4": draw_four, "5": draw_five, "6": draw_six, "7": draw_seven, "8": draw_eight, "9": draw_nine}

        for num in final_score: #final score is a string.
            glColor3f(0.0, 0.0, 1.0)
            if num == "1":
                numbers[num](score_coords[0], score_coords[1], scoreHeight=100) # we are updating the key value of the numbers dictionary. 0 represent X AND 1 represent Y.
                score_coords[0] += 10 #increasing score coordinates by 10.
            else:
                numbers[num](score_coords[0], score_coords[1], scoreWidth=40, scoreHeight=100) #if the num is not '1',updating the dicitonary then we are increasing the scroe by 50.
                score_coords[0] += 50

    if paused == True and gameOver == False: #if the game is in pause state.
        for i in range(len(pauseBoxCoords)):
            boxCoord1 = np.matmul(translatePauseCoords, pauseBoxCoords[i])  #creating pause box overall.
            boxCoord2 = np.matmul(translatePauseCoords, pauseBoxCoords[(i + 1) % len(pauseBoxCoords)])
            glColor3f(0.0, 1.0, 0.0)
            drawLine(boxCoord1[0][0], boxCoord1[1][0], boxCoord2[0][0], boxCoord2[1][0]) #[1][0]  REPRESENT Y COORDINATES. SIMILARLY VICE VERSA.

        if (timesScaled == 0):
            coords = np.matmul(translatePauseCoords, pauseBoxCoords[0]) #(a,b) means a * b
            x_coord = coords[0][0] #creating the x and y coordinates.
            y_coord = coords[1][0]
            start_coords = [x_coord + 40, y_coord - 5]
            letters = {"P": drawP, "A": drawA, "U": drawU, "S": drawS, "E": drawE, "D": drawD} #creating the letters using the pause box.
            text = "PAUSED"
            for letter in text:
                letters[letter](start_coords[0], start_coords[1])
                start_coords[0] += 40

        if (timesScaled > 0):
            for i in range(len(pauseBoxCoords)): #updating the iterator.
                pauseBoxCoords[i] = np.matmul(pauseScale, pauseBoxCoords[i]) #iterator becomes the value.

            timesScaled -= 1 #decreasing the global variable.

    numbers = {"0": draw_zero, "1": draw_one, "2": draw_two, "3": draw_three, "4": draw_four, "5": draw_five,
               "6": draw_six, "7": draw_seven, "8": draw_eight, "9": draw_nine}
    string_score = str(score) #top  left string score.

    #-----------------------------------------------------------------
    current_coords = list(num_coords)
    for num in string_score:
        glColor3f(0.0, 1.0, 0.0)
        numbers[num](current_coords[0], current_coords[1])
        if num == "1":
            current_coords[0] += 10
        else:
            current_coords[0] += scoreWidth + 10

    string_level = str(level) #shows the level number.
    current_level = list(level_points) #putting the points in list.
    for num in string_level:
        if num == "1":
            current_level[0] -= 10 #decreasing the current level value.
        else:
            current_level[0] -= (scoreWidth + 10) #increasing the current level value.

    for num in string_level:
        glColor3f(0.0, 0.0, 1.0)
        numbers[num](current_level[0], current_level[1]) #updating the key value in the number dictionary.

        if num == "1":
            current_level[0] += 10 #increasing the current level
        else:
            current_level[0] += (scoreWidth + 10)

    if ((circle_points[0][0] + radius >= width) or (circle_points[0][0] - radius <= 0)): #if the circle points with radius is greater than width or if it negative.
        translateVector[:, 2] = np.matmul(reflect_y, translateVector[:, 2]) #we are reflecting the points along y-axis. i.e when the ball touches the sidebars.

    if (circle_points[1][0] + radius >= height):
        translateVector[:, 2] = np.matmul(reflect_x, translateVector[:, 2]) # if the ball touches the top boundary ,we will reflect the ball along x axis.

    glColor3f(0.8, 0.8, 0.8)
    if (paused == False and gameOver == False):
        circle_points = np.matmul(translateVector, circle_points)
    for i in range(board_points[1][0]): #now we are creating the board points.
        drawLine(board_points[0][0], board_points[1][0] - i - 1, board_points[0] + board_width, board_points[1] - i - 1)
    glColor3f(0.8, 0.8, 0.8)
    r = radius

    while r > 0: #if the radius is greater than 0.
        values = draw_circle(r)
        for value in values:
            draw_points(value[0] + circle_points[0][0], value[1] + circle_points[1][0])
        r -= 1

    if (paused == False and gameOver == False):
        if (circle_points[1][0] - radius <= board_points[1][0] and startGame == True): #if the points are less or equal to the board points and the game has already started.
            if (circle_points[0][0] + radius >= board_points[0][0] and circle_points[0][0] <= board_points[0][0] + board_width):# if the points are greater than radius and the circle point itself is less or equal than board width.
                translateVector[:, 2] = np.matmul(reflect_x, translateVector[:, 2]) #reflecting the coordinates along the x axis.
                translateVector[0, 2] = (circle_points[0][0] - (board_points[0][0] + board_width // 2)) // 10  #returns floating value.

            elif (circle_points[0][0] - radius <= board_points[0][0] + board_width and circle_points[0][0] >=
                  board_points[0][0]):# if the points are greater than radius and the circle point itself is equal than board width.
                translateVector[:, 2] = np.matmul(reflect_x, translateVector[:, 2]) #reflecting along the x-axis.
                translateVector[0, 2] = (circle_points[0][0] - (board_points[0][0] + board_width // 2)) // 10  #returns  float value.

        if (translateVector[0][2] >= 0 and translateVector[1][2] >= 0):
            getx = math.floor(circle_points[0][0] / block_width)
            nextx = getx + 1  #next point the ball will move
            prevx = getx - 1  #previous point the ball has moved.

            first_y = blocks.get(getx) #blockes is list.

            if (first_y != None):
                i = 0
                b = len(first_y) #traversing the list using len function.
                while i < b:
                    if (radius + circle_points[1][0] <= (first_y[i] + 1) * block_height and radius + circle_points[1][
                        0] >= first_y[i] * block_height): #using the both conditions.
                        first_y.pop(i) #popping the value out from the list.
                        if (reversed == False):
                            translateVector[:, 2] = np.matmul(reflect_x, translateVector[:, 2]) #reflecting the value along x axis.
                            reversed = True #toggling the reverse variable.
                        b -= 1 #decreasing the length
                        score += blockPoint #increasing the score points.
                    else:
                        i += 1

                if (len(first_y) == 0):
                    blocks.pop(getx) #if the length becomes 0 then pop out the iterator.

            second_y = blocks.get(nextx) #doing the same process for the next point in which the circle will move.
            if (second_y != None):
                i = 0
                b = len(second_y)
                while i < b:
                    if (radius + circle_points[1][0] <= (second_y[i] + 1) * block_height and radius + circle_points[1][
                        0] >= second_y[i] * block_height and radius + circle_points[0][0] >= nextx * block_width):
                        second_y.pop(i)
                        if (reversed == False):
                            translateVector[:, 2] = np.matmul(reflect_y, translateVector[:, 2])
                            reversed = True
                        score += blockPoint
                        b -= 1
                    elif (-radius * math.sin(math.radians(135)) + circle_points[1][0] <= (
                            second_y[i] + 1) * block_height and -radius * math.sin(math.radians(135)) +
                          circle_points[1][0] >= second_y[i] * block_height and radius + circle_points[0][
                              0] >= nextx * block_width):
                        second_y.pop(i)
                        if (reversed == False):
                            translateVector[:, 2] = np.matmul(reflect_y, translateVector[:, 2])
                            reversed = True
                        b -= 1
                        score += blockPoint
                    else:
                        i += 1

                if (len(second_y) == 0):
                    blocks.pop(nextx)

            third_y = blocks.get(prevx) #using the same process for which the circle had previously moved.
            if (third_y != None):
                i = 0
                b = len(third_y)
                while i < b:
                    if (radius * math.sin(math.radians(45)) + circle_points[1][0] >= third_y[
                        i] * block_height and radius * math.sin(math.radians(45)) + circle_points[1][0] <= (
                            third_y[i] + 1) * block_height and -radius + circle_points[0][
                        0] >= prevx * block_width and -radius + circle_points[0][0] <= (prevx + 1) * block_width):  #using the condition in which the ball will move diagonally.
                        third_y.pop(i)
                        if (reversed == False):
                            translateVector[:, 2] = np.matmul(reflect_x, translateVector[:, 2]) #relecting along x axis.
                            reversed = True
                        b -= 1
                        score += blockPoint
                    else:
                        i += 1

                if (len(third_y) == 0):
                    blocks.pop(prevx)

        elif (translateVector[0][2] < 0 and translateVector[1][2] >= 0): #if the  first row 3rd value is less than 0 and second row 3rd value is greater or equal to 0.
            getx = math.floor(circle_points[0][0] / block_width)
            nextx = getx + 1 #meaning the next point.
            prevx = getx - 1 #meaning the previous point.

            first_y = blocks.get(getx)
            if (first_y != None):   #using the process as before.
                i = 0
                b = len(first_y)
                while i < b:
                    if (radius + circle_points[1][0] <= (first_y[i] + 1) * block_height and radius + circle_points[1][
                        0] >= first_y[i] * block_height):
                        first_y.pop(i)
                        if (reversed == False):
                            translateVector[:, 2] = np.matmul(reflect_x, translateVector[:, 2])
                            reversed = True
                        b -= 1
                        score += blockPoint
                    else:
                        i += 1

                if (len(first_y) == 0):
                    blocks.pop(getx)

            second_y = blocks.get(prevx)
            if (second_y != None):
                i = 0
                b = len(second_y)

                while i < b:
                    if (radius + circle_points[1][0] <= (second_y[i] + 1) * block_height and radius + circle_points[1][
                        0] >= second_y[i] * block_height and circle_points[0][0] - radius <= (prevx + 1) * block_width):
                        second_y.pop(i)
                        if (reversed == False):
                            translateVector[:, 2] = np.matmul(reflect_y, translateVector[:, 2])
                            reversed = True
                        b -= 1
                        score += blockPoint
                    elif (radius * math.sin(math.radians(225)) + circle_points[1][0] <= (
                            second_y[i] + 1) * block_height and radius * math.sin(math.radians(225)) + circle_points[1][
                              0] >= (second_y[i]) * block_height and circle_points[0][0] - radius <= (
                                  prevx + 1) * block_width):
                        second_y.pop(i)
                        if (reversed == False):
                            translateVector[:, 2] = np.matmul(reflect_y, translateVector[:, 2])
                            reversed = True
                        b -= 1
                        score += blockPoint
                    else:
                        i += 1

            third_y = blocks.get(nextx)
            if (third_y != None):
                i = 0
                b = len(third_y)
                while i < b:
                    if (radius * math.sin(math.radians(45)) + circle_points[1][0] >= third_y[
                        i] * block_height and radius * math.sin(math.radians(45)) + circle_points[1][0] <= (
                            third_y[i] + 1) * block_height and radius + circle_points[0][
                        0] >= nextx * block_width and radius + circle_points[0][0] <= (nextx + 1) * block_width):
                        third_y.pop(i)
                        if (reversed == False):
                            translateVector[:, 2] = np.matmul(reflect_x, translateVector[:, 2])
                            reversed = True
                        b -= 1
                        score += blockPoint
                    else:
                        i += 1

                if (len(third_y) == 0):
                    blocks.pop(prevx)

        elif (translateVector[0][2] > 0 and translateVector[1][2] <= 0):
            getx = math.floor(circle_points[0][0] / block_width)
            nextx = getx + 1
            prevx = getx - 1

            first_y = blocks.get(getx)
            if (first_y != None):
                i = 0
                b = len(first_y)
                while i < b:
                    if (-radius + circle_points[1][0] <= (first_y[i] + 1) * block_height and -radius + circle_points[1][
                        0] >= first_y[i] * block_height):
                        first_y.pop(i)
                        if (reversed == False):
                            translateVector[:, 2] = np.matmul(reflect_x, translateVector[:, 2])
                            reversed = True
                        b -= 1
                        score += blockPoint
                    else:
                        i += 1

                if (len(first_y) == 0):
                    blocks.pop(getx)

            second_y = blocks.get(nextx)
            if (second_y != None):
                i = 0
                b = len(second_y)
                while i < b:
                    if (-radius + circle_points[1][0] <= (second_y[i] + 1) * block_height and -radius +
                            circle_points[1][0] >= second_y[i] * block_height and radius + circle_points[0][
                                0] >= nextx * block_width):
                        second_y.pop(i)
                        if (reversed == False):
                            translateVector[:, 2] = np.matmul(reflect_y, translateVector[:, 2])
                            reversed = True
                        score += blockPoint
                        b -= 1
                    elif (radius * math.sin(math.radians(45)) + circle_points[1][0] <= (
                            second_y[i] + 1) * block_height and -radius * math.sin(math.radians(45)) + circle_points[1][
                              0] >= second_y[i] * block_height and radius + circle_points[0][0] >= nextx * block_width):
                        second_y.pop(i)
                        if (reversed == False):
                            translateVector[:, 2] = np.matmul(reflect_y, translateVector[:, 2])
                            reversed = True
                        score += blockPoint
                        b -= 1
                    else:
                        i += 1

                if (len(second_y) == 0):
                    blocks.pop(nextx)

            third_y = blocks.get(prevx)
            if (third_y != None):
                i = 0
                b = len(third_y)
                while i < b:
                    if (radius * math.sin(math.radians(225)) + circle_points[1][0] >= third_y[
                        i] * block_height and radius * math.sin(math.radians(225)) + circle_points[1][0] <= (
                            third_y[i] + 1) * block_height and -radius + circle_points[0][
                        0] >= prevx * block_width and -radius + circle_points[0][0] <= (prevx + 1) * block_width):
                        third_y.pop(i)
                        if (reversed == False):
                            translateVector[:, 2] = np.matmul(reflect_x, translateVector[:, 2])
                            reversed = True
                        b -= 1
                        score += blockPoint
                    else:
                        i += 1

                if (len(third_y) == 0):
                    blocks.pop(prevx)

        elif (translateVector[0][2] < 0 and translateVector[1][2] <= 0):
            getx = math.floor(circle_points[0][0] / block_width)
            nextx = getx + 1
            prevx = getx - 1

            first_y = blocks.get(getx)
            if (first_y != None):
                i = 0
                b = len(first_y)
                while i < b:
                    if (-radius + circle_points[1][0] <= (first_y[i] + 1) * block_height and -radius + circle_points[1][
                        0] >= first_y[i] * block_height):
                        first_y.pop(i)
                        if (reversed == False):
                            translateVector[:, 2] = np.matmul(reflect_x, translateVector[:, 2])
                            reversed = True
                        b -= 1
                        score += blockPoint
                    else:
                        i += 1

                if (len(first_y) == 0):
                    blocks.pop(getx)

            second_y = blocks.get(prevx)
            if (second_y != None):
                i = 0
                b = len(second_y)

                while i < b:
                    if (-radius + circle_points[1][0] <= (second_y[i] + 1) * block_height and -radius +
                            circle_points[1][0] >= second_y[i] * block_height and circle_points[0][0] - radius <= (
                                    prevx + 1) * block_width):
                        second_y.pop(i)
                        if (reversed == False):
                            translateVector[:, 2] = np.matmul(reflect_y, translateVector[:, 2])
                            reversed = True
                        b -= 1
                        score += blockPoint
                    elif (radius * math.sin(math.radians(45)) + circle_points[1][0] <= (
                            second_y[i] + 1) * block_height and radius * math.sin(math.radians(45)) + circle_points[1][
                              0] >= (second_y[i]) * block_height and circle_points[0][0] - radius <= (
                                  prevx + 1) * block_width):
                        second_y.pop(i)
                        if (reversed == False):
                            translateVector[:, 2] = np.matmul(reflect_y, translateVector[:, 2])
                            reversed = True
                        b -= 1
                        score += blockPoint
                    else:
                        i += 1

            third_y = blocks.get(nextx)
            if (third_y != None):
                i = 0
                b = len(third_y)
                while i < b:
                    if (radius * math.sin(math.radians(225)) + circle_points[1][0] >= third_y[
                        i] * block_height and radius * math.sin(math.radians(225)) + circle_points[1][0] <= (
                            third_y[i] + 1) * block_height and radius + circle_points[0][
                        0] >= nextx * block_width and radius + circle_points[0][0] <= (nextx + 1) * block_width):
                        third_y.pop(i)
                        if (reversed == False):
                            translateVector[:, 2] = np.matmul(reflect_x, translateVector[:, 2])
                            reversed = True
                        b -= 1
                        score += blockPoint
                    else:
                        i += 1

                if (len(third_y) == 0):
                    blocks.pop(prevx)

    if (len(blocks.keys()) == 0): # level up and restarting.
        board_points = np.array([[int(width * 0.15)], [10], [1]])
        radius = 5
        startGame = False
        circle_points = np.array([[board_points[0][0] + 60], [board_points[1][0] + radius], [1]])
        translateVector = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        num_blocks += 1
        level += 1
        generate_blocks(num_blocks) #generating the blocks

    reversed = False
    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate()
    glColor3f(1.0, 0.65, 0.0)
    blockScreen()
    updateScreen()
    glutSwapBuffers()


def generate_blocks(num_blocks): #creating the blocks randomly.
    i = 0
    while (i < num_blocks):
        key = random.randint(0, (800 // block_width) - 1)  #using random to create the blocks.
        temp = height // block_height #using var=/temp variable.
        value = random.randint(temp - 16, temp - 8) #using the var variable in the random function to create a value.
        if key not in blocks: #if the value of key is not present in the block dictionary..
            blocks[key] = [value] #value will become key.
            i += 1
        else:
            if (value not in blocks[key]): #if the value is not present ,we add the value in the block dictionary.
                blocks[key].append(value)
                i += 1


def generate_fixed_blocks(num_blocks): #blocks that a fixed.
    i = 0
    key = 0
    while (i < num_blocks):
        temp = height // block_height
        value = random.randint(temp - 16, temp - 8)
        if key not in blocks:
            blocks[key] = [value]
            i += 1
        else:
            if (value not in blocks[key]):
                blocks[key].append(value)
                i += 1

#-----------------------------------------
def mouse_click(button, state, x, y):
    global paused
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        paused = not paused

def mouse_move(x, y):
    global board_points, board_width
    if not paused and not gameOver:
        new_x = x - board_width / 2
        if new_x < 0:
            new_x = 0
        elif new_x > width - board_width:
            new_x = width - board_width
        board_points[0][0] = new_x
        if not startGame:
            circle_points[0][0] = new_x + 60
    glutPostRedisplay()


generate_blocks(num_blocks)
glutInit()
glutInitDisplayMode(GLUT_RGBA)
glutInitWindowSize(width, height)
glutInitWindowPosition(0, 0)
window = glutCreateWindow(b"Block Breaker")
glutDisplayFunc(showScreen)
glutKeyboardFunc(buttons)
glutMouseFunc(mouse_click)
glutPassiveMotionFunc(mouse_move)
glutSpecialFunc(keys)
glutMainLoop()

