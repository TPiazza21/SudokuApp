# this is the file which will include the main algorithmic material
#(so I can keep the web design separate)

import itertools
import random
from copy import copy, deepcopy


def recursiveSearch(trait=3):
    """This method will use backtracking, implemented with recursion, to find a filled in grid of entries
    This method was again heavily inspired by https://codereview.stackexchange.com/questions/88849/sudoku-puzzle-generator
    as well as https://en.wikipedia.org/wiki/Backtracking """

    # m is the width and height of the board
    m = trait * trait
    # have a board that starts out as none
    testBoard = [[None for q in range(m)] for q in range(m)]

    def check(p=0):
        # i is the row number (simply the integer version of p/m)
        i = p // m
        # j is the column number
        j = p % m
        blockRow = i - i % trait
        blockColumn = j - j % trait
        numbers = list(range(1, m + 1))
        random.shuffle(numbers)
        # go through all possible numbers (in random order)
        for candidate in numbers:
            if checkIfValid(candidate, testBoard, i, j, blockRow, blockColumn):
                # if I have satisfied all necessary conditions, then this coordinate can be candidate, so I don't need to check the rest
                testBoard[i][j] = candidate
                # here's the recursion: if the next spot is impossible to fill, then iterate this spot to the next candidate
                if (p + 1) >= m * m or check(p + 1):
                    return testBoard
        else:
            testBoard[i][j] = None
            return None

    return check()


def printBoard(board, m=3):
    """print the board in the command window (I will deal with the actual website image in application.py)"""
    # print a sudoku board, generalized for different m (which is the trait)
    for row in board:
        print(("||" + (" {} |" * m + "|") * m).format(*(cell or ' ' for cell in row)))


def showAvailableNumbers(board, trait=3):
    """ this method will return one list of pairs that represent which spots are open.
    This method will return a second list of possible numbers in those slots
    """
    emptySpots = []
    possibleVals = []
    # these are the row and column of the block that this element is a part of
    n = trait * trait
    for i in range(n):
        for j in range(n):
            # if there is an empty spots
            if board[i][j] == None:
                emptySpots.append([i, j])
                possibleVals.append(findPossibleVals(board, i, j, trait))

    return(emptySpots, possibleVals)


def findPossibleVals(board, i, j, trait=3):
    """
    this method returns the possible numbers for a given empty spot, using basic rules of sudoku
    """
    n = trait * trait
    allVals = list(range(1, n + 1))
    blockRow = i - i % trait
    blockColumn = j - j % trait
    returnedValues = []
    for candidate in allVals:
        if checkIfValid(candidate, board, i, j, blockRow, blockColumn):
            # if I have satisfied all necessary conditions, then this coordinate can be candidate, so I don't need to check the rest
            returnedValues.append(candidate)

    return(returnedValues)


def checkUnique(board, trait=3):
    """ this method checks if a grid, with spots empty, can still be solved
    uniquely (I know that there is at least one solution)"""

    # these are the positions-of-the-empty-spots, as well as the possible-values-of-each-slot
    (emptySpots, possibleVals) = showAvailableNumbers(board, trait)
    maxP = len(emptySpots)
    # you want this number to be NO MORE THAN 1
    checkUnique.validSolutions = 0
    checkUnique.boards = []

    # iterate through all possible numbers that can be in these spots
    def tryAll(p, currentBoard, fillMe):
        # new_Board is a copy of currentBoard (and not just a pointer to where the old board was)
        new_board = deepcopy(currentBoard)
        if p > 0:
            # the line below is to fill the board with what was tried last time
            new_board[emptySpots[p - 1][0]][emptySpots[p - 1][1]] = fillMe

        # define the blockRow and blockColumn again (coordinates of upper left cell in a trait by trait block)
        blockRow = emptySpots[p][0] - emptySpots[p][0] % trait
        blockColumn = emptySpots[p][1] - emptySpots[p][1] % trait

        # go through all possible vals for this p
        for candidate in possibleVals[p]:

            # if you haven't found more validSolutions AND if this is a valid spot AND if you haven't filled all spots yet
            if checkUnique.validSolutions < 2 and checkIfValid(candidate, new_board, emptySpots[p][0], emptySpots[p][1], blockRow, blockColumn):
                if p < maxP - 1:
                    tryAll(p + 1, new_board, candidate)
                elif p == maxP - 1:
                    checkUnique.validSolutions += 1

    tryAll(0, board, 0)
    return (checkUnique.validSolutions % 2)


def makePlayableBoard(board, trait=3):
    """ this method will take a filled in square grid, and iteratively peel off random tiles (and its opposite)"""
    # this statement is to randomly decide if the center tile stays or not. I don't check anything because it's the first tile
    m = trait * trait
    if random.random() < 0.76:
        board[4][4] = None

    # pairs are potential coordinates to remove a value
    pairs = []
    for a in range(m):
        for b in range(a + 1):
            pairs.append([a, b])
    pairs.remove([4, 4])
    random.shuffle(pairs)
    # for now, let's remove 30 values (I may make this more dynamic later)
    for pair in pairs[0:30]:
        # make a copy of the board so you don't alter it
        new_board = deepcopy(board)
        new_board[pair[0]][pair[1]] = None
        # this other measure is to ensure
        new_board[m - pair[0] - 1][m - pair[1] - 1] = None
        # if the board is still unique, make the board have this property
        if checkUnique(new_board, trait):
            board[pair[0]][pair[1]] = None
            board[m - pair[0] - 1][m - pair[1] - 1] = None

    return board


def checkIfValid(candidate, board, i, j, blockRow, blockColumn, trait=3):
    ''' this method sees if a number (candidate) can fit in the board at a given position
    '''
    if (candidate not in board[i]  # check for contradiction in row i
        and all(row[j] != candidate for row in board)  # in column j
            and all(candidate not in row[blockColumn:(blockColumn + trait)] for row in board[blockRow:(blockRow + trait)])):  # for the blocks
        return True
    else:
        # if any of these conditions fail, return false (because this is an invalid number)
        return False


def puzzleToString(board, trait=3):
    ''' this is the inverse of the last method (take a board, make it a string) '''
    m = trait * trait
    boardString = ""

    for row in board:
        for cell in row:
            if cell == None:
                boardString += ""
            else:
                boardString += str(cell)

    return(boardString)


def errorCount(completedString, myString, trait=3):
    ''' this method compared the string of a completed board to a potentially completed board '''
    # if the strings are the same then by golly you've solved the board
    m = trait * trait

    # if the strings are the same, then there are by definition no errors, so send 100 back for the sake of it
    if completedString == myString:
        return 100
    errorCounter = 0
    for i in range(m * m):
        if myString[i] != '0':
            if myString[i] != completedString[i] and myString[i].isdigit():
                errorCounter += 1
    return errorCounter


def rankDifficulty(board, trait=3):
    ''' this method ranks the difficulty of a board based on https://dlbeer.co.nz/articles/sudoku.html
    where he ranks difficulty by number of empty spots plus (b_i - 1)^2 at each node, where b_i is the branching factor
    (i.e. how many options there are) '''

    m = trait * trait
    (emptySpots, branches) = showAvailableNumbers(board, trait)
    difficulty = 0
    # go through every empty spot and apply this formula for difficulty
    for branch in branches:
        difficulty = difficulty + 1 + (len(branch) - 1) * (len(branch) - 1)

    return(difficulty)
