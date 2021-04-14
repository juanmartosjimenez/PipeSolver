import csv
import random
from matrix import Game
from matrix import Type
from matrix import Pipe
from os import path
import sys
import time

sys.setrecursionlimit(10000)


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
            print(toc-tic)
            break


if __name__ == '__main__':
    start_game(130, "game_gen.txt")
