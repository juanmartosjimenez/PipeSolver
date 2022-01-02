# PipeSolver

PipeSolver is an engine that determines the solution of a pipe game via SAT reduction. A pipe game is a grid filled with pipes, a pipe is either straight or right angled, a pipe can be rotated four different ways. To solve the pipe game, the pipes must be connected so that water can flow from top right grid square to the bottom left grid square.

## What is a SAT Reduction Problem?

A boolean satisfiability problem (SAT) consists of determining wether a solution exists for a boolean formula. For example "a ^ b" is satisfied by a=1 and b=1, "a ^ ~a" can't be satisfied. At a simple level these are the fundamentals of an SAT problem, figuring out if each literal can be given a value such that it satisfies the boolean formula. The most challenging part of this project is understanding how to break the game into a series of literal that can then be put into a boolean formula. How does one go about encoding the game into single values that can only represent 1 or 0? It is intriguing how simple the concept of SAT is, yet how elaborate it's applications are.

## Inner Workings of the Script
The script generates a random game board of n by n dimensions. The game is solved two ways, the first is via recursion and the second is via SAT reduction. 

#### Recursion
The algorithm starts at the top right and checks all the possible paths procedurely. If the adjacent pipes are viable paths then it continues down those paths until it reaches a path that is no longer viable or it reaches the destination, in this case the solution has been found.

#### SAT Reduction
The first step is converting the board such that it can be represented by booleans. Each cell is assigned a unique ID, the rotation of the pipe is also assigned a unique ID. A horizontal straight pipe is 1, a vertical straight pipe is 2, a right angle pipe pointing up and to the right is 3 and so on. Through this encoding, each cell can be assigned a unique literal based on its orientation and position.
The next step is creating constraints to enforce the rules of the game, for example:
* For two straight pipes to be connected they must both be horizontal or vertical
* For a winning game the top right and bottom right cells must be connect

These constraints are created for every cell in the grid. The constraints are joined via logic AND's and are solved via the PySat engine. The output is whether the grid is solvable and what the winning path is.

A sample 30x30 board generated can be seen below.

![Sample Board Generated](images/30x30.png?raw=true "Randomly Generated 30x30 Board")

A sample solution for the board above determined via SAT reduction can be seen below.
![Sample Solution for Board](images/30x30Solution.png?raw=true "Solution Via SAT Reduction for 30x30 Board")
