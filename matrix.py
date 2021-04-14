from enum import Enum
from termcolor import colored


class Type(Enum):
    """
    Enum class that represents the three different types of pipes, either turn, straight or empty.
    """
    TURN = 1
    STRAIGHT = 2
    EMPTY = 3


class Pipe:
    """
    Pipe class represents a pipe object, with the type x_cord, y_cord and orientation. Orientation ranges from
    0 to 3 for a turn pipe and from 0 to 1 for a straight pipe.
    """

    def __init__(self, pipe_type: Type, xcord: int, ycord: int, orientation: int = 0):
        """
        Constructor for the pipe class
        :param pipe_type: Type of pipe, one of turn, straight and empty
        :param xcord: x coordinate of pipe
        :param ycord: y coordinate of pipe
        :param orientation: orientation of pipe
        """
        self.type = pipe_type
        self.xcord = xcord
        self.ycord = ycord
        self.color = "black"
        if self.type == Type.TURN:
            if orientation < 0 or orientation > 3:
                raise Exception('Invalid orientation')
        elif self.type == Type.STRAIGHT:
            if orientation < 0 or orientation > 1:
                raise Exception('Invalid orientation')
        self.orientation = orientation

    def __verify_color(self, out):
        if self.color == "black":
            return out
        else:
            return colored(out, color="blue")

    # all pipes ║ ╔ ╗ ╝ ╚ ═
    def __str__(self):
        """
        Called whenever a pipe is printed, prints the pipes given their orientation and color.
        :return: returns a string representation of the pipe
        """
        if self.type == Type.TURN and self.orientation == 0:
            return self.__verify_color("╚ ")
        elif self.type == Type.TURN and self.orientation == 1:
            return self.__verify_color("╔ ")
        elif self.type == Type.TURN and self.orientation == 2:
            return self.__verify_color("╗ ")
        elif self.type == Type.TURN and self.orientation == 3:
            return self.__verify_color("╝ ")
        elif self.type == Type.STRAIGHT and self.orientation == 0:
            return self.__verify_color("║ ")
        elif self.type == Type.STRAIGHT and self.orientation == 1:
            return self.__verify_color("═ ")
        elif self.type == Type.EMPTY:
            return self.__verify_color("· ")
        else:
            raise Exception("Invalid pipe type")

    def __repr__(self):
        """
        Called whenever a pipe is printed, prints the pipes given their orientation and color.
        :return: returns a string representation of the pipe
        """
        if self.type == Type.TURN and self.orientation == 0:
            return self.__verify_color("╚ ")
        elif self.type == Type.TURN and self.orientation == 1:
            return self.__verify_color("╔ ")
        elif self.type == Type.TURN and self.orientation == 2:
            return self.__verify_color("╗ ")
        elif self.type == Type.TURN and self.orientation == 3:
            return self.__verify_color("╝ ")
        elif self.type == Type.STRAIGHT and self.orientation == 0:
            return self.__verify_color("║ ")
        elif self.type == Type.STRAIGHT and self.orientation == 1:
            return self.__verify_color("═ ")
        elif self.type == Type.EMPTY:
            return self.__verify_color("· ")
        else:
            raise Exception("Invalid pipe type")

    def change_orientation(self, new: int):
        """
        changes orientation of pipe
        :param new: new int representation of pipe
        """
        if self.type == Type.TURN:
            if new < 0 or new > 3:
                raise Exception('Invalid orientation')
        elif self.type == Type.STRAIGHT:
            if new < 0 or new > 1:
                raise Exception('Invalid orientation')
        self.orientation = new

    def change_color(self):
        """
        changes color of pipe
        """
        self.color = "blue"

    def copy_pipe(self):
        """
        copies a pipe object
        :return: new pipe object with same fields
        """
        return Pipe(self.type, self.xcord, self.ycord, self.orientation)


class Game:
    def __init__(self, matrix: list):
        """
        constructor for the Game class, keeps track of the game board and all pipes
        :param matrix: the game board to be used with all the pipes
        """
        if matrix is not None and len(matrix) != 0:
            self.matrix = matrix
        else:
            raise Exception("Null or empty matrix")

        self.row = len(matrix)
        self.col = len(matrix[0])

    def valid_coord(self, x_cord, y_cord):
        """
        checks if the given coordinates are valid in the matrix
        :param x_cord: the x coordinate
        :param y_cord: the y coordinate
        :return: true if coordinate is valid else false
        """
        return 0 <= x_cord < self.col and 0 <= y_cord < self.row

    # all pipes ║ ╔ ╗ ╝ ╚ ═
    def to_string(self):
        """
        converts game board to string
        :return: string of game board
        """
        final_str = ""
        for row in self.matrix:
            tmp_str = ""
            for elem in row:
                tmp_str += str(elem)
            final_str += tmp_str + "\n"
        return final_str

    def get_matrix(self):
        """
        getter for the game board
        :return: the game board
        """
        return self.matrix

    def __solve_helper(self, entry_point: int, x_cord: int, y_cord: int, acc=None):
        """
        Solves the game by recursively checking every grid, if grid connects to end point then solution is found
        :param entry_point:entry point into the grid at x_cord, y_cord.
        :param x_cord:the x-coordinate of the grid
        :param y_cord:the y-coordinate of the grid
        :return:a list of lists, one list contains the solution, the rest contain at least one field with false.
        """

        if acc is None:
            acc = []

        if not self.valid_coord(x_cord, y_cord):
            raise Exception("Invalid coordinates")

        tmp_dict = {}
        if [x_cord, y_cord] in acc:
            return tmp_dict
        acc.append([x_cord, y_cord])
        pipe = self.matrix[y_cord][x_cord]
        pipe_type = pipe.type
        destination = [self.col - 1, self.row - 1]

        # if given pipe is in bottom right corner of the graph then check if the game can be finished
        if [x_cord, y_cord] == destination:
            if pipe_type == Type.TURN:
                if entry_point == 0:
                    valid_pipe = pipe.copy_pipe()
                    valid_pipe.change_orientation(0)
                    tmp_dict[valid_pipe] = "destination"
                    return tmp_dict
                else:
                    return False
            elif pipe_type == Type.STRAIGHT:
                if entry_point == 3:
                    valid_pipe = pipe.copy_pipe()
                    valid_pipe.change_orientation(1)
                    tmp_dict[valid_pipe] = "destination"
                    return tmp_dict
                else:
                    return False

        # checks every entry point and pipe type based on that calculates the next possible move
        # entry point is from the top
        elif entry_point == 0:
            if pipe_type == Type.TURN:
                if self.valid_coord(x_cord + 1, y_cord):
                    valid_pipe = pipe.copy_pipe()
                    valid_pipe.change_orientation(0)
                    tmp_dict[valid_pipe] = self.__solve_helper(3, x_cord + 1, y_cord, acc)
                if self.valid_coord(x_cord - 1, y_cord):
                    valid_pipe = pipe.copy_pipe()
                    valid_pipe.change_orientation(3)
                    tmp_dict[valid_pipe] = self.__solve_helper(1, x_cord - 1, y_cord, acc)
            elif pipe_type == Type.STRAIGHT:
                if self.valid_coord(x_cord, y_cord + 1):
                    valid_pipe = pipe.copy_pipe()
                    valid_pipe.change_orientation(0)
                    tmp_dict[valid_pipe] = self.__solve_helper(0, x_cord, y_cord + 1, acc)
            elif pipe_type == Type.EMPTY:
                pass

        # entry point is from the right
        elif entry_point == 1:
            if pipe_type == Type.TURN:
                if self.valid_coord(x_cord, y_cord - 1):
                    valid_pipe = pipe.copy_pipe()
                    valid_pipe.change_orientation(0)
                    tmp_dict[valid_pipe] = self.__solve_helper(2, x_cord, y_cord - 1, acc)
                if self.valid_coord(x_cord, y_cord + 1):
                    valid_pipe = pipe.copy_pipe()
                    valid_pipe.change_orientation(1)
                    tmp_dict[valid_pipe] = self.__solve_helper(0, x_cord, y_cord + 1, acc)
            elif pipe_type == Type.STRAIGHT:
                if self.valid_coord(x_cord - 1, y_cord):
                    valid_pipe = pipe.copy_pipe()
                    valid_pipe.change_orientation(1)
                    tmp_dict[valid_pipe] = self.__solve_helper(1, x_cord - 1, y_cord, acc)
            elif pipe_type == Type.EMPTY:
                pass

        # entry point is from the bottom
        elif entry_point == 2:
            if pipe_type == Type.TURN:
                if self.valid_coord(x_cord + 1, y_cord):
                    valid_pipe = pipe.copy_pipe()
                    valid_pipe.change_orientation(1)
                    tmp_dict[valid_pipe] = self.__solve_helper(3, x_cord + 1, y_cord, acc)
                if self.valid_coord(x_cord - 1, y_cord):
                    valid_pipe = pipe.copy_pipe()
                    valid_pipe.change_orientation(2)
                    tmp_dict[valid_pipe] = self.__solve_helper(1, x_cord - 1, y_cord, acc)
            elif pipe_type == Type.STRAIGHT:
                if self.valid_coord(x_cord, y_cord - 1):
                    valid_pipe = pipe.copy_pipe()
                    valid_pipe.change_orientation(0)
                    tmp_dict[valid_pipe] = self.__solve_helper(2, x_cord, y_cord - 1, acc)
            elif pipe_type == Type.EMPTY:
                pass

        # entry point is from the left
        elif entry_point == 3:
            if pipe_type == Type.TURN:
                if self.valid_coord(x_cord, y_cord - 1):
                    valid_pipe = pipe.copy_pipe()
                    valid_pipe.change_orientation(3)
                    tmp_dict[valid_pipe] = self.__solve_helper(2, x_cord, y_cord - 1, acc)
                if self.valid_coord(x_cord, y_cord + 1):
                    valid_pipe = pipe.copy_pipe()
                    valid_pipe.change_orientation(2)
                    tmp_dict[valid_pipe] = self.__solve_helper(0, x_cord, y_cord + 1, acc)

            elif pipe_type == Type.STRAIGHT:
                if self.valid_coord(x_cord + 1, y_cord):
                    valid_pipe = pipe.copy_pipe()
                    valid_pipe.change_orientation(1)
                    tmp_dict[valid_pipe] = self.__solve_helper(3, x_cord + 1, y_cord, acc)
            elif pipe_type == Type.EMPTY:
                pass
        return tmp_dict

    def __retrieve_path(self, dictionary: dict, prev_item: Pipe = None, acc=None):
        """
        helper that recursively gets path that leads to the endpoint if not found returns an empty list
        :param dictionary: nested dictionary with multiple paths
        :param prev_item: previous item in the loop used to determine if end of recursively call has been reached
        :param acc: accumulator that adds to output
        :return: correct path from start to end necessary to win the game
        """
        if acc is None:
            acc = []
        for key, val in dictionary.items():
            if type(val) is dict:
                acc = self.__retrieve_path(val, prev_item=key)
                if acc:
                    acc.append(key)
                    if prev_item is None:
                        acc.reverse()
                    return acc
            else:
                if val == "destination":
                    acc.append(key)
                    return acc
                else:
                    return False

    def get_winning_path(self):
        """
        gets the winning path for the game board
        :return: list with the winning path
        """
        entry_point = 0
        dictionary = self.__solve_helper(entry_point, 0, 0)
        if dictionary:
            return self.__retrieve_path(dictionary)
        else:
            return []

    def generate_path(self, moves: list):
        """
        generates the given path on the game board
        :param moves: list of moves to be generated on the board
        :return: a board with blue pipes that show the moves generated
        """
        for elem in moves:
            if self.valid_coord(elem.xcord, elem.ycord):
                pipe = self.matrix[elem.ycord][elem.xcord]
                pipe.change_color()
                pipe.change_orientation(elem.orientation)
            else:
                raise Exception("Invalid move attempt")
