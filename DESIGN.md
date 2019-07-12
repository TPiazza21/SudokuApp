Tyler Piazza

I wil describe each method, and I will use capital letters when one method uses another.
Note that my methods are gathered in the "helpers.py" file, wheras the flask application is in "application.py".
Also be aware that the 'trait' is unique to the type of sudoku puzzle - my website displays 9x9 grids, but you could concievably play with 4x4,16x16,etc. boards (n^2 x n^2 boards in general). I kept the trait for my puzzles as trait=3, and m was just trait squared.

Here is the basic application structure of my website:
application.py

@app.route("/")
In "application.py", I start in index() by generating a filled in valid puzzle, which is really just a 9 by 9 array of numbers, which follows the rules of sudoku. I perform this task with RECURSIVESEARCH() (I will talk about this function later).
I then turn this filled in puzzle into a playable puzzle (i.e. I remove some numbers while making sure that the puzzle is still unique), with the method MAKEPLAYABLEBOARD(). I also record the string representation of the finished board, using the method PUZZLETOSTRING().
This string representation is just an 81 character word with 0s where there are blanks and the corresponding number when there are not. This string will appear later when I compare boards for accuracy. I then record the board's difficulty, using the method RANKDIFFICULTY().
Finally, I render the sudoku.html template with the playable board, the trait, and the difficulty sent to it.

@app.route("/score")
This route is called by the javaScript when a person checks the number of errors that they have made.
I first retrieve the boardString, which is the string representation of the person's current board (where they may have input their own guesses).
I then compute the number of errors with ERRORCOUNT() (which, I will define later). I return the number of errors as a json to the html to display.\

Now that I have described the basis web application structure, I will describe helpers.py.

helpers.py

RECURSIVESEARCH()
is a method that generates a filled in square sudoku grid (remember that in our case, trait = 3, but the algorithm works for any trait). As I cite, I read along with parts of
https://codereview.stackexchange.com/questions/88849/sudoku-puzzle-generator, which suggested that I use a recursive form of backtracking. What this means is that I start with a blank board, then place a random number in the first spot. If
my board is still a valid board (i.e. there are no rules broken in sudoku already, for columns, rows, blocks), then I go to the next spot and place a number. I continue like this until I make a new board or I reach a contradiction, at which I will go to the previous square
and try a different tile. This process repeats until a fully solved board is generated. Originally, I had a method that would throw away the entire board if there was a contradiction, and that method took about 30 seconds to generate a full board. This method takes less than a second.
Note that the method CHECKIFVALID is used to verify that the rules of sudoku would not be broken, and I will define this function later.

PRINTBOARD()
is a method made purely for testing purposes. It just prints out a board in the command line so that I could experiment with board generation. It is not used in the final product for anything besides a debugging tool.

SHOWAVAILABLENUMBERS()
is a method that returns an ordered pair, of all coordinates of empty spots in a board and the set of all possible numbers for each empty spot. In other words, the ith element of each list correspond to the same empty element: it's coordinates and its possible values.
The empty spots are easily found by treking through the board and finding spots when the board is None. The possible values are computed in the next method, FINDPOSSIBLEVALS(). At the end, this ordered pair is returned.

FINDPOSSIBLEVALS()
is a method that, given an empty spot in a board, returns all numbers that right now could go in this spot and satisfy the basic rules of sudoku.
These numbers are found by testing all 9 numbers; if a candidate does not break any rule, it is added to the list. Then this list is returned.
Note that the length of this list is bi, the branching factor for the difficulty calcuation (which I will define later).

CHECKUNIQUE()
is a method that checks to see if a board is uniquely solveable. This method's strategy is to basically range over all possible values of all empty spots, and see if there are more than 1 valid solutions.
If I just wanted 1 solution, I would use backtracking again (which would be much faster), but this board comes from a solveable board with hints missing, so the existence of 1 solution is already known.
This method uses the reslts of SHOWAVAILABLENUMBERS() to find empty spots and their possible values, and then ranges over all of them, checking each time if the rules of sudoku are met. If all spots are filled and all rules of sudoku are satisfied,
then you have a winner, so you add it to the tally of validSolutions. If there are 2 valid solutions, then the method tryAll() within checkunique() will end shortly because there is an if statement before every next level that stops if there are more than 1 solutions.

MAKEPLAYABLEBOARD()
is the method that takes a filled in square sudoky grid, and makes it a playable, unique sudoku grid.
I wanted the board to end up being symmetric under 180 degree rotations (for asthetic purposes), so instead of randomly peeling off single elements, I remove one element and then it symmetric pair.
Therefore, the piece in the middle is special beacuse it doesn't have a pair, so to avoid having to constantly check if I am dealing with the middle piece, I have a random chance at the beginning that it is taken off (and this probability is arbitary).
Then, I compile a list of cells that comprise half the board. Next, I try to remove a given cell (and its symmetric pair), and check if I still have a unique solution, using CHECKUNIQUE().
Ultimately, it is this uniqueness condition that takes the most time when computing a playable board, and if I had more time, I would find ways to save redundant calculations.
If the resulting board is not unique, then this pair of elements is no longer considered. Otherwise, the pair of cells is removed from the board.
I repeat for 30 cells (arbitarily), and then I return the unique board.

CHECKIFVALID()
is the method that actually checks that a number can fit in a cell without locally breaking the rules of sudoku.
The column is checked for the candidate, the row is checked for the candidate, and elements in its block are checked for the candidate.
If the candidate satisfies all conditions, then return True. Otherwise, return False.

PUZZLETOSTRING()
is a method that takes a puzzle (a 9x9 array of numbers or Nones) to an 81 character string of 0s where there are spaces and corresponding digits when there are digits.
This method very simply enacts what I just described, and returns this string.

ERRORCOUNT()
takes in two board strings - one of the completely solved board, and one of a potentially missolved board.
If the strings are the same, the player has successfully solved the board, so return 100 (arbitarily).
If the strings differ, then count how many times there are differences that do not involve zero (because the zeros correspond to where the player is unsure).
The count of these differences is the number of times that the player was simply incorrect.
Then, return this error count.

RANKDIFFICULTY()
ranks the difficulty of a playable board. There are many ways to compute difficulty of a board (there does not seem to be a clear standard), but this way seemed computationally straightforward:
a board is more difficult if it has more empty spots, and if it has more initial possible options for each empty spot. These options are weighted by how far away from 1 they are. Clearly, if a board just has 1 possible number in all of the empty spots, then it is a trivial board (very easy to solve).
However, if there are 9 possible options, this particular spot will take some time to deduce. 2 possible options should not just be proportionally related to how 9 possible options hits the difficulty (beacuse 2 options is easy to sovle), so the formula
difficulty = (# empty_spots) + (sum of (bi - 1)(bi - 1)), where bi is the number of possible options of each empty spot, was born. From my method
SHOWAVAILABLENUMBERS(), these bi are just the length of the elements of the possible values.

Lastly, I will discuss the html and javascript (all located on sudoku.html and styles.css, except for the fact that the layout comes from layout.html).

I use much of the style and layout from the c$50 financial trading app, which I copied into layout.html and styles.css. I also found some style code (which I cite) that helps me shade the boxes of the sudoku grid correctly.
In sudoku.html, I have a 9x9 grid of input boxes, which are the cells of the sudoku puzzle. They are either read only (the hints), or not, which is where the empty spots are. People can input up to 5 characters.
There is also a button called "How am I doing", which will use ajax to send to the server the current string that represents the player's board, and the data that returns is the number of errors (as I have discussed).
When constructing this string, I ignore elements with more than 1 character (because the person is still deciding). I then take the feedback of errors according to their meaning (and pring out the results).
I also display the difficulty at the top, just for the sake of letting people know what caliber puzzle they are trying to solve.
Also note that when someone clicks on the "Sudoku" in the upper left corner, they are taken to a new puzzle.

