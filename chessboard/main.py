import queue
import matplotlib.pyplot as plt
import numpy as np
import time

knight_moves = [
    [-2, 1], [-2, -1],
    [2, 1], [2, -1],
    [1, 2], [-1, 2],
    [1, -2], [-1, -2]
]


def get_square_x(i):
    return [i, i + 1, i + 1, i]


def get_square_y(j):
    return [j, j, j + 1, j + 1]


def redraw_board():
    board = np.zeros((8, 8))
    plt.imshow(board, cmap='grey', extent=(0, 8, 0, 8))
    for i in range(8):
        for j in range(8):
            if (i + j) % 2 == 0:
                plt.fill(get_square_x(i), get_square_y(j), color='white', alpha=1)
            else:
                plt.fill(get_square_x(i), get_square_y(j), color='black', alpha=1)


def visualize_chessboard(path):
    for move in path:
        redraw_board()
        plt.fill(get_square_x(move[0]), get_square_y(move[1]), color='#8B4513', alpha=0.8)
        plt.show()
        time.sleep(1.5)


def valid_position(position):
    return 0 <= position[0] < 8 and 0 <= position[1] < 8


def validate_input(user_input):
    input_parts = user_input.split()
    return len(input_parts) == 2 and all(part.isdigit() for part in input_parts)


def gen_knight_moves(position, visited_positions):
    possible_moves = []
    x, y = position

    for move in knight_moves:
        new_x = x + move[0]
        new_y = y + move[1]
        if valid_position((new_x, new_y)) and visited_positions[new_x][new_y] == 0:
            visited_positions[new_x][new_y] = 1
            possible_moves.append((new_x, new_y))
    return possible_moves


def show_shortest_path(shortest_path):
    print(" -> ".join(map(str, shortest_path)))


def find_path(start, end):
    if not valid_position(start) or not valid_position(end):
        raise ValueError("Invalid position")

    to_explore = queue.Queue()
    to_explore.put(start)
    visited = [[0 for _ in range(8)] for _ in range(8)]
    predecessors = [[None for _ in range(8)] for _ in range(8)]

    while not to_explore.empty():

        cur_x, cur_y = to_explore.get()

        if (cur_x, cur_y) == end:
            break

        possible_moves = gen_knight_moves([cur_x, cur_y], visited)

        for move in possible_moves:
            predecessors[move[0]][move[1]] = (cur_x, cur_y)
            to_explore.put(move)

    shortest_path = []

    # should never happen
    if predecessors[end[0]][end[1]] is None and start != end:
        print("No path found")
        return

    while end != start:
        shortest_path.insert(0, end)
        end = predecessors[end[0]][end[1]]

    shortest_path.insert(0, start)
    show_shortest_path(shortest_path)
    visualize_chessboard(shortest_path)


def read_input():
    start_position = tuple(map(int, input("Enter starting position (x y): ").split()))
    end_position = tuple(map(int, input("Enter ending position (x y): ").split()))
    return start_position, end_position


if __name__ == '__main__':
    try:
        start_pos, end_pos = read_input()
        find_path(start_pos, end_pos)
    except ValueError as e:
        print(e)
