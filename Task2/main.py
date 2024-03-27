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
SHUFFLE = 2
# Colors ---------------------------------------------------------------------------------------------------------------
DARK = pygame.Color(250, 235, 215)
LIGHT = pygame.Color(139, 69, 19)
RED = pygame.Color(220, 20, 60)
BLACK = pygame.Color(0, 0, 0)
COLORS = {'w': LIGHT, 'b': DARK, 'q': RED}
MOVES = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
# Global variables -----------------------------------------------------------------------------------------------------
maze = np.array([])
N = 0
GOOD_ENOUGH = 2


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
    pygame.display.set_caption("N Queens problem - Hill Climbing Algorithm")
    redraw()


def set_label(iterations):
    pygame.draw.rect(screen, BLACK, (20, screen_height - OFFSET_FOR_RESULTS, screen_width, OFFSET_FOR_RESULTS))
    font = pygame.font.Font(None, 80)
    label1 = font.render("Iterations : " + str(iterations), True, LIGHT)
    screen.blit(label1, (20, screen_height - OFFSET_FOR_RESULTS + 20))
    pygame.display.flip()


def set_label_done(iterations):
    set_label(iterations)
    pygame.draw.rect(screen, BLACK, (20, screen_height - 80, screen_width, OFFSET_FOR_RESULTS))
    font = pygame.font.Font(None, 80)
    label2 = font.render("Done!", True, LIGHT)
    screen.blit(label2, (20, screen_height - 80))
    pygame.display.flip()


def visualize(old_positions, new_positions):
    check_events()
    global maze
    for i in range(len(old_positions)):
        x, y = old_positions[i]
        if (x + y) % 2 == 0:
            maze[y][x] = 'b'
        else:
            maze[y][x] = 'w'

    for i in range(len(new_positions)):
        x, y = new_positions[i]
        maze[y][x] = 'q'
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
    if len(sys.argv) != 4:
        raise "Usage python3 main.py <N> <neighbour_method1-3> <visualization>"
    global N
    N = int(sys.argv[1])

    return int(sys.argv[2]), bool(int(sys.argv[3]))


# HELPER FUNCTIONS  ----------------------------------------------------------------------------------------------------
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
    threats = 0

    for i in range(len(queen_positions)):
        for j in range(i + 1, len(queen_positions)):
            if are_threatened(queen_positions[i], queen_positions[j]):
                threats += 1

    return threats


def position_threats(pos, queen_positions):
    threats = 0

    for q_pos in queen_positions:
        if are_threatened(pos, q_pos) and pos is not q_pos:
            threats += 1

    return threats


def getPossibleMoves(i, queen_positions, old_threats, hoops_allowed=0):
    possible_moves = []
    old_pos = queen_positions[i]

    # set out of board for no threats
    queen_positions[i] = (N + 1, N + 1)

    for move in MOVES:
        x, y = old_pos
        while 0 <= x + move[0] < N and 0 <= y + move[1] < N:
            x += move[0]
            y += move[1]

            new_threats = position_threats((x, y), queen_positions)

            if (x, y) in queen_positions:
                if hoops_allowed:
                    continue
                break

            # assume the direction is non-perspective (needed for bigger boards)
            if new_threats > old_threats: break
            possible_moves.append((x, y))

    queen_positions[i] = old_pos
    return possible_moves


def get_random_position(state, old_threat):
    # gets random position with better or the same threats
    x, y = np.random.randint(0, N), np.random.randint(0, N)

    while (x, y) in state or position_threats((x, y), state) > old_threat:
        x, y = np.random.randint(0, N), np.random.randint(0, N)

    return x, y


def get_most_threatened(state):
    ids, threats = [], 0

    for i in range(len(state)):
        cur_threats = position_threats(state[i], state)
        if cur_threats > threats:
            ids.clear()
            ids.append(i)
            threats = cur_threats
        elif cur_threats == threats:
            ids.append(i)

    return ids[np.random.randint(0, len(ids))], threats


def chess_move(queen_positions, hoops_allowed=0):
    old_state_threats = objective_function(queen_positions)
    best_threats, best_i, best_move = None, None, None

    for i in range(len(queen_positions)):
        old_threats = position_threats(queen_positions[i], queen_positions)
        possible_moves = getPossibleMoves(i, queen_positions, old_threats, hoops_allowed)

        for move in possible_moves:
            old = queen_positions[i]
            queen_positions[i] = move

            new_threats = objective_function(queen_positions)

            if best_move is None or new_threats < best_threats:
                best_threats, best_i, best_move = new_threats, i, move

            queen_positions[i] = old

            # used for bigger boards, to cut through the search space
            if new_threats < old_state_threats - GOOD_ENOUGH:
                queen_positions[best_i] = best_move
                return queen_positions

    if best_i is not None:
        queen_positions[best_i] = best_move

    return queen_positions


def chess_move_with_hoops(queen_positions):
    return chess_move(queen_positions, hoops_allowed=1)


def valid_chess_move(queue_positions):
    return chess_move(queue_positions, hoops_allowed=0)


def best_threat_move(queen_positions):
    # this function is using just the position_threats not objective_function to determine the best move
    q_id, old_threat = get_most_threatened(queen_positions)
    best = queen_positions[q_id]
    queen_positions.remove(queen_positions[q_id])
    it = 1

    for i in range(len(queen_positions)):
        for j in range(len(queen_positions)):
            current = i, j
            if current not in queen_positions:
                new_threats = position_threats(current, queen_positions)
                if new_threats < old_threat:
                    queen_positions.append(current)
                    return queen_positions

                elif new_threats == old_threat and np.random.randint(0, it) == 0:
                    best = current
        it += 1
    queen_positions.append(best)

    return queen_positions


# HILL CLIMBING --- ----------------------------------------------------------------------------------------------------
def hill_climbing(state, get_neighbour_state, visualization=False):
    threats = objective_function(state)
    iterations = 0

    while threats > 0:
        old_state = state.copy()
        best_neighbour = get_neighbour_state(state)
        new_threats = objective_function(best_neighbour)

        if new_threats < threats:
            state = best_neighbour
            threats = new_threats
            print("Threats", threats)
        else:
            for _ in range(SHUFFLE):
                q_id, most_threats = get_most_threatened(state)
                state.remove(state[q_id])
                state.append(get_random_position(state, most_threats))
                threats = objective_function(state)

        iterations += 1
        set_label(iterations)

        if visualization:
            sleep(0.3)
            visualize(old_state, state)

    return state, iterations


def main():
    global maze
    method, visualization = read_input()

    # dont shadow name
    match method:
        case 1:
            neighbour_method = valid_chess_move
        case 2:
            neighbour_method = chess_move_with_hoops
        case 3:
            neighbour_method = best_threat_move
        case _:
            raise "Invalid method"

    state = get_random_state()
    gen_maze_from_positions(state)
    calculate_screen_size()
    screen_init()

    state, iterations = hill_climbing(state, neighbour_method, visualization)

    gen_maze_from_positions(state)
    set_label_done(iterations)
    while True:
        check_events()
        redraw()


if __name__ == '__main__':
    main()
