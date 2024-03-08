import os
import random
from time import sleep
import pygame
import sys
from queue import Queue, PriorityQueue
import numpy as np


class ArgumentsError(Exception):
    pass


# Constants ------------------------------------------------------------------------------------------------------------
CELL_SIZE = 20
SLEEP_TIME = 0
# adjust the screen size to your needs
SCREEN_WIDTH, SCREEN_HEIGHT = 3840, 2160
PADDING = 150
OFFSET_FOR_RESULTS = 150

# Colors
WHITE = (255, 255, 255)  # Fresh
GREY = (128, 128, 128)  # Wall
BLUE = (0, 0, 255)  # Open
GREEN = (0, 255, 0)  # Closed
RED = (255, 0, 0)  # Path
YELLOW = (255, 255, 0)  # Start
PURPLE = (128, 0, 128)  # End
BLACK = (0, 0, 0)

COLORS = {' ': WHITE, 'X': GREY, 'o': BLUE, 'c': GREEN, 'p': RED, 's': YELLOW, 'e': PURPLE}

NEIGHBOURS = {(0, 1), (0, -1), (1, 0), (-1, 0)}

# Global variables -----------------------------------------------------------------------------------------------------
maze = np.array([])
screen = pygame.display.set_mode((1200, 800))
screen_width, screen_height = 1200, 800
step = False


# Visualization --------------------------------------------------------------------------------------------------------

def draw_maze():
    for y in range(len(maze)):
        for x in range(len(maze[y])):
            color = COLORS[maze[y][x]]
            pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def draw_step(x, y):
    stepper() if step else sleep(SLEEP_TIME)
    color = COLORS[maze[y][x]]
    pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.display.flip()
    check_events()


def visualize_path(path, start, end):
    expanded = np.count_nonzero((maze == 'c') | (maze == 'o'))

    maze[start[::-1]] = 's'
    maze[end[::-1]] = 'e'
    draw_step(*start), draw_step(*end)

    for vertex in path:
        maze[vertex[::-1]] = 'p'
        draw_step(*vertex)

    # Draw labels
    font = pygame.font.Font(None, 80)
    label1 = font.render("Shortest path length : " + str(len(path) - 1), True, WHITE)
    label2 = font.render("Expanded nodes : " + str(expanded), True, WHITE)
    screen.blit(label1, (20, screen_height - OFFSET_FOR_RESULTS + 10))
    screen.blit(label2, (20, screen_height - 80))
    pygame.display.flip()


def calculate_screen_size():
    global CELL_SIZE
    cols, rows = len(maze[0]), len(maze)
    CELL_SIZE = min((SCREEN_WIDTH - PADDING) // cols,
                    (SCREEN_HEIGHT - OFFSET_FOR_RESULTS - PADDING) // rows)


def screen_init(start, end, algo):
    global screen, screen_height, screen_width
    cols, rows = len(maze[0]), len(maze)

    os.environ['SDL_VIDEO_CENTERED'] = '1'
    screen_width, screen_height = cols * CELL_SIZE, rows * CELL_SIZE + OFFSET_FOR_RESULTS
    screen = pygame.display.set_mode((screen_width, screen_height), )
    pygame.display.set_caption("State Space Exploring Algorithms : " + algo.__name__)

    maze[start[::-1]] = 's'
    maze[end[::-1]] = 'e'
    redraw()
    sleep(1)


def check_flip_maze(start, end):
    global maze

    if len(maze[0]) < len(maze):
        maze = maze.transpose()
        return start[::-1], end[::-1]

    return start, end


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


def stepper():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


def do_nothing():
    pass


# Reading input --------------------------------------------------------------------------------------------------------
def read_input(filename):
    start, end = None, None
    tmp_maze = []
    with open(filename, 'r') as file:
        for line in file:
            row = line.strip()
            if "start" in row:
                start = tuple(map(int, row.replace("start", "").split(", ")))
            elif "end" in row:
                end = tuple(map(int, row.replace("end", "").split(", ")))
            else:
                tmp_maze.append(list(row))
    global maze
    maze = np.array(tmp_maze)

    return start, end


def read_args():
    global SLEEP_TIME, step

    if len(sys.argv) <= 4:
        raise ArgumentsError("Usage: python main.py <filename> <{bfs,dfs,a*,greedy,random}> <{snail,slow,fast}> <{"
                             "step,auto}>")

    filename, algo, speed, stepping = sys.argv[1:]
    step = True if stepping == "step" else False

    match speed:
        case "snail":
            SLEEP_TIME = 1
        case "slow":
            SLEEP_TIME = 0.1
        case "fast":
            SLEEP_TIME = 0
    return filename, algo, stepping


# Helper functions -----------------------------------------------------------------------------------------------------
def valid_position(x, y):
    return 0 <= x < len(maze[0]) and 0 <= y < len(maze) and maze[y][x] != 'X' and maze[y][x] != 'c'


def get_neighbours(current):
    neighbours = []
    for neighbour in NEIGHBOURS:
        x = current[0] + neighbour[0]
        y = current[1] + neighbour[1]
        if valid_position(x, y):
            neighbours.append((x, y))
    return neighbours


def backtrace(parent, end):
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = parent[current]
    return path[::-1]


def euclidean_distance(a, b):
    return np.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


# BFS ------------------------------------------------------------------------------------------------------------------
def bfs(start, end):
    q = Queue()
    visited = set()
    parent = {start: None}

    # init
    q.put(start)
    visited.add(start)

    while not q.empty():
        current = q.get()

        if current == end:
            break

        for neighbour in get_neighbours(current):
            if neighbour not in visited:
                q.put(neighbour)
                visited.add(neighbour)
                parent[neighbour] = current

                maze[neighbour[::-1]] = 'o'
                draw_step(*neighbour)

        maze[current[::-1]] = 'c'
        draw_step(*current)

    return backtrace(parent, end)


# A*  ------------------------------------------------------------------------------------------------------------------
def a_star(start, end, heuristic=euclidean_distance):
    q = PriorityQueue()
    visited = set()
    parent = {}
    dist = {}

    # init
    q.put((0, start))
    dist[start] = 0
    parent[start] = None
    visited.add(start)

    while not q.empty():
        _, current = q.get()

        if current == end:
            maze[current[::-1]] = 'c'
            draw_step(*current)
            break

        # returns neighbours that are not closed and are not wall
        for neighbour in get_neighbours(current):
            distance = dist[current] + 1
            if neighbour not in visited or distance < dist[neighbour]:
                dist[neighbour] = distance
                q.put((distance + heuristic(neighbour, end), neighbour))
                visited.add(neighbour)
                parent[neighbour] = current

                maze[neighbour[::-1]] = 'o'
                draw_step(*neighbour)

        maze[current[::-1]] = 'c'
        draw_step(*current)

    return backtrace(parent, end)


# Greedy ---------------------------------------------------------------------------------------------------------------
def greedy_search(start, end, heuristic=euclidean_distance):
    q = PriorityQueue()
    visited = set()
    parent = {}

    # init
    q.put((0, start))
    parent[start] = None
    visited.add(start)

    while not q.empty():
        _, current = q.get()

        if current == end:
            break

        for neighbour in get_neighbours(current):
            if neighbour not in visited:
                q.put((heuristic(neighbour, end), neighbour))
                visited.add(neighbour)
                parent[neighbour] = current

                maze[neighbour[::-1]] = 'o'
                draw_step(*neighbour)

        maze[current[::-1]] = 'c'
        draw_step(*current)

    return backtrace(parent, end)


# RandomSearch ---------------------------------------------------------------------------------------------------------
def random_search(start, end):
    q = list()
    visited = set()
    parent = {start: None}

    # init
    q.append(start)
    visited.add(start)

    while not len(q) == 0:
        idx = random.randint(0, len(q) - 1)
        current = q[idx]
        del q[idx]

        if current == end:
            break

        for neighbour in get_neighbours(current):
            if neighbour not in visited:
                q.append(neighbour)
                visited.add(neighbour)
                parent[neighbour] = current

                maze[neighbour[::-1]] = 'o'
                draw_step(*neighbour)

        maze[current[::-1]] = 'c'
        draw_step(*current)

    return backtrace(parent, end)


# DFS ------------------------------------------------------------------------------------------------------------------
def dfs(start, end):
    visited = set()
    stack = [(start, False)]
    parent = {start: None}

    while len(stack) != 0:
        current, can_close = stack.pop()
        maze[current[::-1]] = 'o'
        draw_step(*current)

        if current == end:
            break

        if can_close:
            maze[current[::-1]] = 'c'
            draw_step(*current)
            continue

        visited.add(current)
        stack.append((current, True))

        for neighbour in get_neighbours(current):
            if neighbour not in visited:
                stack.append((neighbour, False))
                parent[neighbour] = current

    return backtrace(parent, end)


def main():
    pygame.init()
    algorithms = {'bfs': bfs, 'dfs': dfs, 'a*': a_star, 'greedy': greedy_search, 'random': random_search}

    try:
        filename, algo, stepping = read_args()
        start, end = read_input(filename)
        start, end = check_flip_maze(start, end)
        algorithm = algorithms[algo]
        calculate_screen_size()
        screen_init(start, end, algorithm)

        path = algorithm(start, end)
        visualize_path(path, start, end)

    except Exception as e:
        print(e)
        return

    # Main loop
    while True:
        check_events()


if __name__ == "__main__":
    main()
