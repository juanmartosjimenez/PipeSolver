import csv
import math
import random
from matrix import Game
from matrix import Type
from matrix import Pipe
from os import path
import sys
import time

sys.setrecursionlimit(10000)
clauses = []


def get_matrix(filename):
    """
    generates game based on an input file
    :param filename: file to be read from
    :return: a list of lists representing the game
    """
    if not path.exists(filename):
        raise Exception("File does not exist")

    parsed_game = []
    with open(filename) as f:
        game = csv.reader(f, delimiter=',')
        for row in game:
            parsed_game.append([int(elem) for elem in row])

    first_row = parsed_game.pop(0)
    num_rows = first_row[0]
    num_cols = first_row[1]

    for ii, row in enumerate(parsed_game):
        xcord = row[0]
        ycord = row[1]
        if not (num_cols > xcord >= 0):
            raise Exception("Invalid x coordinate")
        if not (num_rows > ycord >= 0):
            raise Exception("Invalid y coordinate")

    game_matrix = []
    for row in range(num_cols):
        tmp_row = []
        for col in range(num_rows):
            pipe_type = Type.EMPTY
            for entry in parsed_game:
                if entry[0] == col and entry[1] == row:
                    pipe_type = Type(entry[2])

            tmp_row.append(Pipe(pipe_type, col, row))

        game_matrix.append(tmp_row)
    return Game(game_matrix)


def gen_random_game(size: int, filename: str = "game_gen.txt"):
    """
    generates a random game and saves to a file
    :param size: size of the game board
    :param filename: name of the file to be saved to
    """
    tmp_str = str(size) + ", " + str(size) + "\n"
    for ii in range(size):
        for jj in range(size):
            tmp_str += str(ii) + ", " + str(jj) + ", " + str(random.randint(1, 2)) + "\n"
    with open(filename, "w") as f:
        f.write(tmp_str)


def start_game(dimension, filename="game_gen.txt"):
    """
    method starts game
    :param dimension: dimension of the game to be generated
    :param filename: file to be generated
    """
    while True:
        gen_random_game(dimension, filename)
        game = get_matrix(filename)
        tic = time.perf_counter()
        winning_path = game.get_winning_path()
        if winning_path:
            print(game.to_string())
            game.generate_path(winning_path)
            toc = time.perf_counter()
            print(game.to_string())
            print(toc - tic)
            break


# gets the index with the correct number of padded 0's
def get_index(dim, ii):
    cells = dim*dim
    ii = str(ii)
    return ii.zfill(len(str(cells)))


# Each cell in the grid is represented by a single integer i, the function get_coordinates returns the correct x and y
# value for the given i value based on the size of the grid.
def get_coordinates(dim, i):
    x_val = i % dim
    y_val = math.floor(i / dim)

    return x_val, y_val


def create_constraints():
    dimension = 5  # creates a 3 by 3 game
    cells = dimension * dimension  # Represents the number of cells in the grid
    filename = "sat_game.txt"
    # gen_random_game(dimension, filename)
    game = get_matrix(filename)

    # ensures that all coordinates in matrix are valid
    for ii in range(cells):
        x, y = get_coordinates(dimension, ii)
        if not game.valid_coord(x, y):
            raise Exception("Error with matrix creation")

    matrix = game.get_matrix()

    # create constraints to ensure that each cell has one pipe type either ═:1 ║:2 ╔:3 ╗:4 ╝:5 ╚:6
    for ii in range(cells):
        x, y = get_coordinates(dimension, ii)
        ii_index = get_index(dimension, ii)

        if matrix[y][x].type == Type.STRAIGHT:
            # has to be one orientation either 1 or 2
            clauses.append([ii_index + "1", ii_index + "2"])
            # can't be both orientations at same time, negation of 1 ^ 2 is -1 ∨ -2
            clauses.append(["-" + ii_index + "1", "-" + ii_index + "2"])
        elif matrix[y][x].type == Type.TURN:
            # has to be either 3, 4, 5, 6
            clauses.append([ii_index + "3", ii_index + "4", ii_index + "5", ii_index + "6"])
            # can only be one
            for jj in range(3, 7):
                for kk in range(jj + 1, 7):
                    clauses.append(["-" + ii_index + str(jj), "-" + ii_index + str(kk)])
        else:
            raise Exception("Invalid Pipe when creating constraints")

    # create constraints for source pipe
    if matrix[0][0].type == Type.STRAIGHT:
        start_index = get_index(dimension, 0)
        clauses.append([start_index + "2"])
    elif matrix[0][0].type == Type.TURN:
        start_index = get_index(dimension, 0)
        clauses.append([start_index+"6"])

    # create constraints for destination pipe
    if matrix[dimension-1][dimension-1] == Type.STRAIGHT:
        start_index = get_index(dimension, cells-1)
        clauses.append([start_index+"1"])
    elif matrix[dimension-1][dimension-1].type == Type.TURN:
        start_index = get_index(dimension, cells-1)
        clauses.append([start_index+"6"])

    # define interactions between pipes in adjacent cells
    for ii in range(cells):
        x, y = get_coordinates(dimension, ii)
        ii_index = get_index(dimension, ii)

        if matrix[y][x].type == Type.STRAIGHT:
            # check for surrounding cells and clauses for each situation
            # top cell
            if game.valid_coord(x)


if __name__ == '__main__':
    create_constraints()
