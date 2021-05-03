# PipeSolver

A script capable of solving any pipe game, the pipe game is a grid filled with pipes. The user can rotate the pipes and the goal is to get water to flow from point A, the top left corner of the grid to point B, the bottom right corner of the grid. The script randomly generates a pipe game and checks to see if a solution exists. If a solution exists, it finds the path that solves the game via an algorithm that uses SAT reduction. 

To run the program, first clone the repository, then install the necessary libraries, Pysat and termcolor. Once this libraries are installed run the program using python3 main.py. The only required input is the dimension of the grid to be generated, the output will be the randomly generated grid, the solved grid via an algorithm and the solved grid via the SAT solver.
