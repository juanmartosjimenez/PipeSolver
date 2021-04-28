import csv
import math
import random
from matrix import Game
from matrix import Type
from matrix import Pipe
from os import path
import sys
import time
from pysat.solvers import Glucose4

sys.setrecursionlimit(10000)
clauses = []
visited = []


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


def gen_random_game_helper(size: int, filename: str = "game_gen.txt"):
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


def gen_random_game(dimension=5, filename="game_gen.txt"):
    """
    method starts game
    :param filename: file to be generated
    """
    while True:
        gen_random_game_helper(dimension, filename)
        game = get_matrix(filename)
        winning_path = game.get_winning_path()
        if winning_path:
            break
    return game


def solve_algorithm(dimension=5, filename="game_gen.txt"):
    game = get_matrix(filename)
    winning_path = game.get_winning_path()
    game.generate_path(winning_path)
    print(game.to_string())


# gets the index with the correct number of padded 0's
def get_index(dim, ii):
    cells = dim * dim
    ii = str(ii)
    return "1" + ii.zfill(len(str(cells)))


# gets the integer index from the x and y positions
def get_int_index(dim, x, y):
    return y * dim + x


# Each cell in the grid is represented by a single integer i, the function get_coordinates returns the correct x and y
# value for the given i value based on the size of the grid.
def get_coordinates(dim, i):
    x_val = i % dim
    y_val = math.floor(i / dim)

    return x_val, y_val


def parse_solution(game, solution):
    """
    generates path in grid from solution returned from the sat solver
    Parameters
    ----------
    game game object
    solution array containing correct orientations of each pipe

    Returns
    -------

    """
    matrix = game.get_matrix()
    for ii, elem in enumerate(solution):
        x, y = get_coordinates(game.col, ii)
        pipe = matrix[y][x]
        rot = int(str(elem)[-1])
        # ═:1 ║:2 ╔:3 ╗:4 ╝:5 ╚:6
        if pipe.type == Type.TURN:
            if rot == 3:
                pipe.change_orientation(1)
            elif rot == 4:
                pipe.change_orientation(2)
            elif rot == 5:
                pipe.change_orientation(3)
            elif rot == 6:
                pipe.change_orientation(0)
            else:
                raise Exception("turn pipe invalid orientation")
        elif pipe.type == Type.STRAIGHT:
            if rot == 1:
                pipe.change_orientation(1)
            elif rot == 2:
                pipe.change_orientation(0)
            else:
                raise Exception("straight pipe invalid orientation")
    print(game.to_string())


def sat_helper(game, ii, entry):
    dimension = game.col
    cells = dimension * dimension
    matrix = game.get_matrix()
    x, y = get_coordinates(dimension, ii)
    acc = []
    if ii in visited:
        return
    visited.append(ii)

    # skip the source and destination to avoid creating unnecessary constraints
    # if (x == 0 and y == 0) or (ii == cells - 1):
    #   continue

    ii_index = get_index(dimension, ii)

    if matrix[y][x].type == Type.STRAIGHT:
        # check for surrounding cells and create clauses for each situation

        # ═:1 ║:2 ╔:3 ╗:4 ╝:5 ╚:6
        # first cell
        if ii == 0:
            if game.valid_coord(x, y + 1):
                ii_bottom = get_int_index(dimension, x, y + 1)
                ii_string_bottom = get_index(dimension, ii_bottom)
                pipe_bottom = matrix[y + 1][x]
                sat_helper(game, ii_bottom, 0)
                if pipe_bottom.type == Type.TURN:
                    clauses.append([int(ii_string_bottom + "6"), int("-" + ii_index + "2")])
                elif pipe_bottom.type == Type.STRAIGHT:
                    clauses.append([int(ii_string_bottom + "2"), int("-" + ii_index + "2")])
                return [[ii_bottom, 0]]

        # last cell
        if ii == cells - 1:
            if game.valid_coord(x - 1, y):
                return []

        # top cell/bottom cell
        if (entry == 0 or entry == 2) and game.valid_coord(x, y - 1) and game.valid_coord(x, y + 1):
            ii_top = get_int_index(dimension, x, y - 1)
            ii_bottom = get_int_index(dimension, x, y - 1)
            ii_string_top = get_index(dimension, ii_top)
            ii_string_bottom = get_index(dimension, ii_bottom)

            pipe_top = matrix[y - 1][x]
            pipe_bottom = matrix[y + 1][x]
            # curr2 -> (top3 or top4 or top2) ^ (bottom5 or bottom6 or bottom2)
            # ═:1 ║:2 ╔:3 ╗:4 ╝:5 ╚:6

            if entry == 2:
                sat_helper(game, ii_top, 2)
                acc.append([ii_top, 2])
                if pipe_top.type == Type.TURN:
                    clauses.append([int(ii_string_top + "4"), int(ii_string_top + "3"), int("-" + ii_index + "2")])
                # curr2 -> (top3
                elif pipe_top.type == Type.STRAIGHT:
                    clauses.append([int(ii_string_top + "2"), int("-" + ii_index + "2")])
                else:
                    raise Exception("unexpected pipe")

            if entry == 0:
                sat_helper(game, ii_bottom, 0)
                acc.append([ii_bottom, 0])
                if pipe_bottom.type == Type.TURN:
                    clauses.append(
                        [int(ii_string_bottom + "5"), int(ii_string_bottom + "6"), int("-" + ii_index + "2")])
                elif pipe_bottom.type == Type.STRAIGHT:
                    clauses.append([int(ii_string_bottom + "2"), int("-" + ii_index + "2")])
                else:
                    raise Exception("unexpected pipe")
        else:
            # do nothing for now
            pass  # TODO

        # right cell/left cell
        if (entry == 1 or entry == 3) and game.valid_coord(x + 1, y) and game.valid_coord(x - 1, y):
            ii_right = get_int_index(dimension, x + 1, y)
            ii_left = get_int_index(dimension, x - 1, y)
            ii_string_right = get_index(dimension, ii_right)
            ii_string_left = get_index(dimension, ii_left)

            pipe_left = matrix[y][x - 1]
            pipe_right = matrix[y][x + 1]

            # ═:1 ║:2 ╔:3 ╗:4 ╝:5 ╚:6

            if entry == 3:
                sat_helper(game, ii_right, 3)
                acc.append([ii_right, 3])
                if pipe_right.type == Type.TURN:
                    if game.valid_coord(x + 1, y - 1) and game.valid_coord(x + 1, y + 1):
                        clauses.append(
                            [int(ii_string_right + "4"), int(ii_string_right + "5"), int("-" + ii_index + "1")])
                    elif game.valid_coord(x + 1, y - 1):
                        clauses.append(
                            [int(ii_string_right + "5"), int("-" + ii_index + "1")])
                    elif game.valid_coord(x + 1, y + 1):
                        clauses.append(
                            [int(ii_string_right + "4"), int("-" + ii_index + "1")])


                elif pipe_right.type == Type.STRAIGHT:
                    clauses.append([int(ii_string_right + "1"), int("-" + ii_index + "1")])
                else:
                    raise Exception("unexpected pipe")

            if entry == 1:
                sat_helper(game, ii_left, 1)
                acc.append([ii_left, 1])
                if pipe_left.type == Type.TURN:
                    clauses.append(
                        [int(ii_string_left + "3"), int(ii_string_left + "6"), int("-" + ii_index + "1")])
                elif pipe_left.type == Type.STRAIGHT:
                    clauses.append([int(ii_string_left + "1"), int("-" + ii_index + "1")])
                else:
                    raise Exception("unexpected pipe")
        else:
            pass  # TODO
            # if not ((x == 0 and y == 0) or (ii == cells - 1)):
            # clauses.append([int("-"+ii_index+"1")])

    elif matrix[y][x].type == Type.TURN:
        # check for surrounding cells and create clauses for each situation

        # first cell
        if ii == 0:
            if game.valid_coord(x + 1, y):
                ii_right = get_int_index(dimension, x + 1, y)
                ii_string_right = get_index(dimension, ii_right)
                pipe_right = matrix[y][x + 1]
                sat_helper(game, ii_right, 3)
                if pipe_right.type == Type.TURN:
                    clauses.append([int(ii_string_right + "4"), int("-" + ii_index + "6")])
                elif pipe_right.type == Type.STRAIGHT:
                    clauses.append([int(ii_string_right + "1"), int("-" + ii_index + "6")])
                return [[ii_right, 3]]

        # last cell
        if ii == cells - 1:
            if game.valid_coord(x, y - 1):
                ii_top = get_int_index(dimension, x, y - 1)
                ii_string_top = get_index(dimension, ii_top)
                pipe_top = matrix[y - 1][x]
                if pipe_top.type == Type.TURN:
                    clauses.append([int(ii_string_top + "4"), int("-" + ii_index + "6")])
                elif pipe_top.type == Type.STRAIGHT:
                    clauses.append([int(ii_string_top + "2"), int("-" + ii_index + "6")])
                    pass
                return [[ii_top, 2]]

        # ═:1 ║:2 ╔:3 ╗:4 ╝:5 ╚:6
        # left cell/top cell
        if (entry == 0 or entry == 3) and game.valid_coord(x, y - 1) and game.valid_coord(x - 1, y):
            ii_top = get_int_index(dimension, x, y - 1)
            ii_left = get_int_index(dimension, x - 1, y)
            ii_string_top = get_index(dimension, ii_top)
            ii_string_left = get_index(dimension, ii_left)

            pipe_left = matrix[y][x - 1]
            pipe_top = matrix[y - 1][x]
            if entry == 3:
                sat_helper(game, ii_top, 2)
                acc.append([ii_top, 2])
                if pipe_top.type == Type.STRAIGHT:
                    clauses.append([int(ii_string_top + "2"), int("-" + ii_index + "5")])
                elif pipe_top.type == Type.TURN:
                    clauses.append([int(ii_string_top + "3"), int(ii_string_top + "4"), int("-" + ii_index + "5")])
                else:
                    raise Exception("invalid pipe")

            if entry == 0:
                sat_helper(game, ii_left, 1)
                acc.append([ii_left, 1])
                if pipe_left.type == Type.STRAIGHT:
                    clauses.append([int(ii_string_left + "1"), int("-" + ii_index + "5")])
                elif pipe_left.type == Type.TURN:
                    clauses.append([int(ii_string_left + "6"), int(ii_string_left + "3"), int("-" + ii_index + "5")])
                else:
                    raise Exception("Invalid pipe")

        else:
            pass  # TODO

        # top cell/right cell
        if (entry == 0 or entry == 1) and game.valid_coord(x + 1, y) and game.valid_coord(x, y - 1):
            ii_top = get_int_index(dimension, x, y - 1)
            ii_right = get_int_index(dimension, x + 1, y)
            ii_string_top = get_index(dimension, ii_top)
            ii_string_right = get_index(dimension, ii_right)

            pipe_top = matrix[y - 1][x]
            pipe_right = matrix[y][x + 1]
            # ═:1 ║:2 ╔:3 ╗:4 ╝:5 ╚:6
            if entry == 1:
                sat_helper(game, ii_top, 2)
                acc.append([ii_top, 2])
                if pipe_top.type == Type.STRAIGHT:
                    clauses.append([int(ii_string_top + "2"), int("-" + ii_index + "6")])
                elif pipe_top.type == Type.TURN:
                    clauses.append([int(ii_string_top + "3"), int(ii_string_top + "4"), int("-" + ii_index + "6")])
                else:
                    raise Exception("invalid pipe")

            if entry == 0:
                sat_helper(game, ii_right, 3)
                acc.append([ii_right, 3])
                if pipe_right.type == Type.STRAIGHT:
                    clauses.append([int(ii_string_right + "1"), int("-" + ii_index + "6")])
                elif pipe_right.type == Type.TURN:
                    clauses.append([int(ii_string_right + "4"), int(ii_string_right + "5"), int("-" + ii_index + "6")])
                else:
                    raise Exception("Invalid pipe")

        else:
            pass  # TODO

        # bottom cell/right cell
        if (entry == 1 or entry == 2) and game.valid_coord(x, y + 1) and game.valid_coord(x + 1, y):
            ii_bottom = get_int_index(dimension, x, y + 1)
            ii_right = get_int_index(dimension, x + 1, y)
            ii_string_bottom = get_index(dimension, ii_bottom)
            ii_string_right = get_index(dimension, ii_right)

            pipe_bottom = matrix[y + 1][x]
            pipe_right = matrix[y][x + 1]

            if entry == 1:
                # ═:1 ║:2 ╔:3 ╗:4 ╝:5 ╚:6
                sat_helper(game, ii_bottom, 0)
                acc.append([ii_bottom, 0])
                if pipe_bottom.type == Type.STRAIGHT:
                    clauses.append([int(ii_string_bottom + "2"), int("-" + ii_index + "3")])
                elif pipe_bottom.type == Type.TURN:
                    clauses.append(
                        [int(ii_string_bottom + "6"), int(ii_string_bottom + "5"), int("-" + ii_index + "3")])
                else:
                    raise Exception("invalid pipe")

            if entry == 2:
                sat_helper(game, ii_right, 3)
                acc.append([ii_right, 3])
                if pipe_right.type == Type.STRAIGHT:
                    clauses.append([int(ii_string_right + "1"), int("-" + ii_index + "3")])
                elif pipe_right.type == Type.TURN:

                    clauses.append([int(ii_string_right + "4"), int(ii_string_right + "5"), int("-" + ii_index + "3")])
                else:
                    raise Exception("Invalid pipe")

        else:
            pass  # TODO

        # left cell/bottom cell
        if (entry == 3 or entry == 2) and game.valid_coord(x - 1, y) and game.valid_coord(x, y + 1):
            ii_bottom = get_int_index(dimension, x, y + 1)
            ii_left = get_int_index(dimension, x - 1, y)
            ii_string_bottom = get_index(dimension, ii_bottom)
            ii_string_left = get_index(dimension, ii_left)

            pipe_bottom = matrix[y + 1][x]
            pipe_left = matrix[y][x - 1]

            # ═:1 ║:2 ╔:3 ╗:4 ╝:5 ╚:6
            if entry == 3:
                sat_helper(game, ii_bottom, 0)
                acc.append([ii_bottom, 0])
                if pipe_bottom.type == Type.STRAIGHT:
                    clauses.append([int(ii_string_bottom + "2"), int("-" + ii_index + "4")])
                elif pipe_bottom.type == Type.TURN:
                    if game.valid_coord(x + 1, y + 1) and game.valid_coord(x - 1, y + 1):
                        clauses.append(
                            [int(ii_string_bottom + "6"), int(ii_string_bottom + "5"), int("-" + ii_index + "4")])
                    elif game.valid_coord(x + 1, y + 1):
                        clauses.append(
                            [int(ii_string_bottom + "6"), int("-" + ii_index + "4")])
                    elif game.valid_coord(x - 1, y + 1):
                        clauses.append(
                            [int(ii_string_bottom + "5"), int("-" + ii_index + "4")])

                else:
                    raise Exception("invalid pipe")

            if entry == 2:
                sat_helper(game, ii_left, 1)
                acc.append([ii_left, 1])
                if pipe_left.type == Type.STRAIGHT:
                    clauses.append([int(ii_string_left + "1"), int("-" + ii_index + "4")])
                elif pipe_left.type == Type.TURN:
                    clauses.append([int(ii_string_left + "6"), int(ii_string_left + "3"), int("-" + ii_index + "4")])
                else:
                    raise Exception("Invalid pipe")
        else:
            pass  # TODO

    else:
        raise Exception("Unexpected pipe type")

    return acc


def solve_sat(dimension=5, filename="test.txt"):
    cells = dimension * dimension  # Represents the number of cells in the grid
    # gen_random_game(dimension, filename)
    game = get_matrix(filename)

    # ensures that all coordinates in matrix are valid
    for ii in range(cells):
        x, y = get_coordinates(dimension, ii)
        if get_int_index(dimension, x, y) != ii:
            raise Exception("Get int index function failed")

        if not game.valid_coord(x, y):
            raise Exception("Error with matrix creation")

    matrix = game.get_matrix()

    # create constraints for source pipe
    if matrix[0][0].type == Type.STRAIGHT:
        start_index = get_index(dimension, 0)
        clauses.append([int(start_index + "2")])
    elif matrix[0][0].type == Type.TURN:
        start_index = get_index(dimension, 0)
        clauses.append([int(start_index + "6")])

    # create constraints for destination pipe
    if matrix[dimension - 1][dimension - 1].type == Type.STRAIGHT:
        start_index = get_index(dimension, cells - 1)
        clauses.append([int(start_index + "1")])
    elif matrix[dimension - 1][dimension - 1].type == Type.TURN:
        start_index = get_index(dimension, cells - 1)
        clauses.append([int(start_index + "6")])

    # create constraints to ensure that each cell has one pipe type either ═:1 ║:2 ╔:3 ╗:4 ╝:5 ╚:6
    for ii in range(cells):
        x, y = get_coordinates(dimension, ii)
        ii_index = get_index(dimension, ii)

        if matrix[y][x].type == Type.STRAIGHT:
            # has to be one orientation either 1 or 2
            clauses.append([int(ii_index + "1"), int(ii_index + "2")])
            # can't be both orientations at same time, negation of 1 ^ 2 is -1 ∨ -2
            clauses.append([int("-" + ii_index + "1"), int("-" + ii_index + "2")])
        elif matrix[y][x].type == Type.TURN:
            # has to be either 3, 4, 5, 6
            clauses.append([int(ii_index + "3"), int(ii_index + "4"), int(ii_index + "5"), int(ii_index + "6")])
            # can only be one
        else:
            raise Exception("Invalid Pipe when creating constraints")

        for jj in range(0, 7):
            for kk in range(jj + 1, 7):
                clauses.append([int("-" + ii_index + str(jj)), int("-" + ii_index + str(kk))])

    # define interactions between pipes in adjacent cells
    sat_helper(game, 0, 0)

    g = Glucose4()
    [g.add_clause(elem) for elem in clauses]

    g.solve()

    try:
        solution = g.get_model()
        pos_sol = []
        for elem in solution:
            if elem >= 0:
                pos_sol.append(elem)
        parse_solution(game, pos_sol)
    except TypeError as e:
        print("No solution found via sat")

    return game


def main():
    while True:
        dim = input("input dimension for game board to be generated between 1 to 100\n")
        try:
            dim = int(dim)
            if 0 >= dim  or dim > 100:
                print("pleasure input valid dimension")
                continue
            else:
                break
        except ValueError as e:
            print("Please make sure dimension is positive integer")

    print("original game board:")
    print(gen_random_game(dim, "test.txt").to_string())
    print("solution via algorithm:")
    solve_algorithm(dim, "test.txt")
    print("solution via sat solver:")
    solve_sat(dim, "test.txt")



if __name__ == '__main__':
    main()
