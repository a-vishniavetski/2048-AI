import random
import constants as c
import numpy as np
from time import perf_counter_ns

# timer decorator
def timer(func):
    def wrapper(*args, **kwargs):
        start = perf_counter_ns()
        result = func(*args, **kwargs)
        end = perf_counter_ns()
        print(f"{func.__name__.upper():<9} took {(end-start):<7} ns == {(end-start)/1_000_000:.8f} ms")
        return result
    return wrapper


def new_game(n):
    matrix = np.zeros((n, n), dtype=int)
    matrix = add_two(matrix)
    matrix = add_two(matrix)
    return matrix


def add_two(mat):
    a = random.randint(0, len(mat)-1)
    b = random.randint(0, len(mat)-1)
    while mat[a][b] != 0:
        a = random.randint(0, len(mat)-1)
        b = random.randint(0, len(mat)-1)
    mat[a][b] = 2
    return mat


def game_state(mat):
    """1 == win, 0 == not over, -1 == lose"""
    # check for win cell
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            if mat[i][j] == 2048:
                return 1
    # check for any zero entries
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            if mat[i][j] == 0:
                return 0
    # check for same cells that touch each other
    for i in range(len(mat)-1):
        # intentionally reduced to check the row on the right and below
        # more elegant to use exceptions but most likely this will be their solution
        for j in range(len(mat[0])-1):
            if mat[i][j] == mat[i+1][j] or mat[i][j+1] == mat[i][j]:
                return 0
    for k in range(len(mat)-1):  # to check the left/right entries on the last row
        if mat[len(mat)-1][k] == mat[len(mat)-1][k+1]:
            return 0
    for j in range(len(mat)-1):  # check up/down entries on last column
        if mat[j][len(mat)-1] == mat[j+1][len(mat)-1]:
            return 0
    return -1


def reverse(mat):
    new = np.zeros((len(mat), len(mat[0])), dtype=int)
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            # new[i].append(mat[i][len(mat[0])-j-1])
            new[i][j] = mat[i][len(mat[0])-j-1]
    return new


def transpose(mat):
    new = np.zeros((len(mat), len(mat[0])), dtype=int)
    for i in range(len(mat[0])):
        for j in range(len(mat)):
            # new[i].append(mat[j][i])
            new[i][j] = mat[j][i]
    return new


# The way to do movement is compress -> merge -> compress again
# Basically if they can solve one side, and use transpose and reverse correctly they should
# be able to solve the entire thing just by flipping the matrix around
# Check the down one. Reverse/transpose if ordered wrongly will give you wrong result.

def cover_up(mat):
    new = np.zeros((len(mat), len(mat[0])), dtype=int)
    done = False
    for i in range(c.GRID_LEN):
        count = 0
        for j in range(c.GRID_LEN):
            if mat[i][j] != 0:
                new[i][count] = mat[i][j]
                if j != count:
                    done = True
                count += 1
    return new, done

def merge(mat, done):
    for i in range(c.GRID_LEN):
        for j in range(c.GRID_LEN-1):
            if mat[i][j] == mat[i][j+1] and mat[i][j] != 0:
                mat[i][j] *= 2
                mat[i][j+1] = 0
                done = True
    return mat, done

@timer
def up(game):
    print("up")
    # return matrix after shifting up
    game = transpose(game)
    game, done = cover_up(game)
    game, done = merge(game, done)
    game = cover_up(game)[0]
    game = transpose(game)
    return game, done

@timer
def down(game):
    print("down")
    # return matrix after shifting down
    game = reverse(transpose(game))
    game, done = cover_up(game)
    game, done = merge(game, done)
    game = cover_up(game)[0]
    game = transpose(reverse(game))
    return game, done

@timer
def left(game):
    print("left")
    # return matrix after shifting left
    game, done = cover_up(game)
    game, done = merge(game, done)
    game = cover_up(game)[0]
    return game, done

@timer
def right(game):
    print("right")
    # return matrix after shifting right
    game = reverse(game)
    game, done = cover_up(game)
    game, done = merge(game, done)
    game = cover_up(game)[0]
    game = reverse(game)
    return game, done

