import os
import sys
from time import sleep

import numpy as np
import pygame

# Constants ------------------------------------------------------------------------------------------------------------
CELL_SIZE = 20
# adjust the screen size to your needs
SCREEN_WIDTH, SCREEN_HEIGHT = 3840, 2160
PADDING = 150
OFFSET_FOR_RESULTS = 150
# Colors ---------------------------------------------------------------------------------------------------------------
WHITE = (255, 255, 255)  # Fresh
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)  # Visited
BLUE = (0, 0, 255)  # Path
RED = (255, 0, 0)  # Start
COLORS = {'w': WHITE, 'b': BLACK, 'q': RED, 'p': BLUE, 'v': GREEN}
MOVES = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
# Global variables -----------------------------------------------------------------------------------------------------
maze = np.array([])
N = 0


# Visualization --------------------------------------------------------------------------------------------------------


def draw_maze():
    for y in range(len(maze)):
        for x in range(len(maze[y])):
            color = COLORS[maze[y][x]]
            pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def calculate_screen_size():
    global CELL_SIZE
    n = len(maze[0])
    CELL_SIZE = min((SCREEN_WIDTH - PADDING) // n,
                    (SCREEN_HEIGHT - OFFSET_FOR_RESULTS - PADDING) // n)


def screen_init():
    global screen, screen_height, screen_width
    cols, rows = len(maze[0]), len(maze)

    pygame.font.init()
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    screen_width, screen_height = cols * CELL_SIZE, rows * CELL_SIZE + OFFSET_FOR_RESULTS
    screen = pygame.display.set_mode((screen_width, screen_height), )
    pygame.display.set_caption("N Queens problem visualization")
    redraw()


def redraw():
    draw_maze()
    pygame.display.flip()
    check_events()


# Pygame - Check Events
def check_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


def generate_maze():
    tmp_maze = np.array([[0] * N] * N, dtype=str)
    for i in range(N):
        for j in range(N):
            if (i + j) % 2 == 0:
                tmp_maze[i][j] = 'b'
            else:
                tmp_maze[i][j] = 'w'
    return tmp_maze


# Reading Input --------------------------------------------------------------------------------------------------------
def read_input():
    if len(sys.argv) != 2:
        raise "Usage python3 main.py <N>"
    global N
    N = int(sys.argv[1])


# HILL CLIMBING---------------------------------------------------------------------------------------------------------
def get_random_state():
    positions = []

    for i in range(N):
        x, y = np.random.randint(0, N), np.random.randint(0, N)
        while (x, y) in positions:
            x, y = np.random.randint(0, N), np.random.randint(0, N)
        positions.append((x, y))

    return positions


def gen_maze_from_positions(positions):
    global maze
    maze = generate_maze()
    for pos in positions:
        x, y = pos
        maze[y][x] = 'q'
    return maze


def are_threatened(pos1, pos2):
    return pos1[0] == pos2[0] or pos1[1] == pos2[1] or abs(pos1[0] - pos2[0]) == abs(pos1[1] - pos2[1])


def objective_function(queen_positions):
    if queen_positions is None:
        return N * 2

    threats = 0

    for i in range(len(queen_positions)):
        for j in range(i + 1, len(queen_positions)):
            if are_threatened(queen_positions[i], queen_positions[j]):
                threats += 1

    return threats


def threats_for_queen(pos, queen_positions):
    threats = 0

    for queen_pos in queen_positions:
        if are_threatened(pos, queen_pos) and pos is not queen_pos:
            threats += 1

    return threats


def get_all_moves(pos, queen_positions):
    possible_moves = []

    for move in MOVES:
        x, y = pos
        while 0 <= x + move[0] < N and 0 <= y + move[1] < N:
            x += move[0]
            y += move[1]

            if (x, y) in queen_positions:
                break

            possible_moves.append((x, y))

    return possible_moves


def getPossibleMoves(pos, queen_positions, old_threats):
    possible_moves = []

    old = queen_positions[queen_positions.index(pos)]

    queen_positions[queen_positions.index(pos)] = (N + 1, N + 1)

    for move in MOVES:
        x, y = pos
        while 0 <= x + move[0] < N and 0 <= y + move[1] < N:
            x += move[0]
            y += move[1]

            if (x, y) in queen_positions or threats_for_queen((x, y), queen_positions) > old_threats:
                break

            possible_moves.append((x, y))

    queen_positions[queen_positions.index((N + 1, N + 1))] = old
    return possible_moves


def get_random_position(state, old_threat):
    x, y = np.random.randint(0, N), np.random.randint(0, N)

    while (x, y) in state or threats_for_queen((x, y), state) > old_threat:
        x, y = np.random.randint(0, N), np.random.randint(0, N)

    return x, y


def get_best_neighbour_state(queen_positions):
    best_threats = N * 2
    best_i, best_move = None, None

    for i in range(len(queen_positions)):
        old_threats = threats_for_queen(queen_positions[i], queen_positions)
        possible_moves = getPossibleMoves(queen_positions[i], queen_positions, old_threats)

        for move in possible_moves:
            old = queen_positions[i]
            queen_positions[i] = move
            new_threats = objective_function(queen_positions)

            if new_threats < best_threats:
                best_threats = new_threats
                best_i = i
                best_move = move

            queen_positions[i] = old

    if best_i is not None:
        queen_positions[best_i] = best_move

    return queen_positions


def hill_climbing():
    state = get_random_state()
    threats = objective_function(state)
    iterations, restarts = 0, 0

    while threats > 0:
        best_neighbour = get_best_neighbour_state(state)
        new_threats = objective_function(best_neighbour)

        if new_threats < threats:
            state = best_neighbour
            threats = new_threats
            print("Threats", threats)
        else:
            restarts += 1
            most_threatened = 0

            for queen in state:
                if threats_for_queen(queen, state) > threats_for_queen(state[most_threatened], state):
                    most_threatened = state.index(queen)

            old_threats = threats_for_queen(state[most_threatened], state)
            state.remove(state[most_threatened])
            state.append(get_random_position(state, old_threats))
            threats = objective_function(state)
        iterations += 1
    return state, iterations, restarts


def main():
    global maze, QueensPositions
    read_input()
    state, iterations, restarts = hill_climbing()

    print("Iterations", iterations, "Restarts", restarts)
    gen_maze_from_positions(state)
    calculate_screen_size()
    screen_init()

    while True:
        check_events()
        redraw()


if __name__ == '__main__':
    main()
