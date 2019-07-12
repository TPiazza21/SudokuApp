import re
from flask import Flask, abort, redirect, render_template, request, jsonify
#from html import escape
from werkzeug.exceptions import default_exceptions, HTTPException
import numpy as np
from helpers import printBoard, recursiveSearch, showAvailableNumbers, checkUnique, makePlayableBoard, puzzleToString, errorCount, rankDifficulty
import time


trait = 3
# this is the trait for this sudoku board (i.e. 9 by 9 board)
m = trait * trait

# this will be the string representation of the board
currentPuzzleString = ""
difficulty = 0

currentPuzzle = [[None for q in range(m)] for q in range(m)]


# Web app
app = Flask(__name__)


@app.after_request
def after_request(response):
    """Disable caching"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    # start the player off with a newly generated board, and save the board's string
    global currentPuzzle
    currentPuzzle = recursiveSearch()
    global currentPuzzleString
    currentPuzzleString = puzzleToString(currentPuzzle)
    makePlayableBoard(currentPuzzle)
    global difficulty
    difficulty = rankDifficulty(currentPuzzle)
    return render_template("sudoku.html", puzzle=currentPuzzle, m=trait, difficulty=difficulty)


@app.route("/score")
def score():
    # this will tell the player how many errors they have made from the correct board
    boardString = request.args.get("sentBoardString")
    global currentPuzzleString
    result = errorCount(currentPuzzleString, boardString)
    return jsonify(result)


@app.errorhandler(HTTPException)
def errorhandler(error):
    """Handle errors"""


# https://github.com/pallets/flask/pull/2314
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
