import random
from time import sleep
import pygame
import sys
from queue import Queue, PriorityQueue
import numpy as np


class ArgumentsError(Exception):
    pass


# Constants ------------------------------------------------------------------------------------------------------------
CELL_SIZE = 7
SLEEP_TIME = 0

# Colors
WHITE = (255, 255, 255)  # Fresh
GREY = (128, 128, 128)  # Wall
BLUE = (0, 0, 255)  # Open
GREEN = (0, 255, 0)  # Closed
RED = (255, 0, 0)  # Path
YELLOW = (255, 255, 0)  # Start
PURPLE = (128, 0, 128)  # End

COLORS = {' ': WHITE, 'X': GREY, 'o': BLUE, 'c': GREEN, 'p': RED, 's': YELLOW, 'e': PURPLE}

NEIGHBOURS = {(0, 1), (0, -1), (1, 0), (-1, 0)}

maze = np.array([])
screen = pygame.display.set_mode((800, 600))


# Visualization --------------------------------------------------------------------------------------------------------

def draw_maze():
    for y in range(len(maze)):
        for x in range(len(maze[y])):
            color = COLORS[maze[y][x]]
            pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def visualize_path(bfs_path, start, end):
    # Show start and end
    maze[start[::-1]] = 's'
    maze[end[::-1]] = 'e'

    animate_move()
    for vertex in bfs_path:
        maze[vertex[::-1]] = 'p'
        animate_move()


# Pygame - Check Events
def check_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


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
    if len(sys.argv) <= 3:
        raise ArgumentsError("Usage: python main.py <filename> <algorithm{bfs,dfs,a*,greedy,random}> <{slow,fast}>")

    filename = sys.argv[1]
    algo = sys.argv[2]
    speed = sys.argv[3]

    if speed == "slow":
        global SLEEP_TIME
        SLEEP_TIME = 0.1

    return filename, algo
# Helper functions -----------------------------------------------------------------------------------------------------
def valid_position(maze, x, y):
    return 0 <= x < len(maze[0]) and 0 <= y < len(maze) and maze[y][x] != 'X' and maze[y][x] != 'c'


def get_neighbours(current):
    neighbours = []
    for neighbour in NEIGHBOURS:
        x = current[0] + neighbour[0]
        y = current[1] + neighbour[1]
        if valid_position(maze, x, y):
            neighbours.append((x, y))
    return neighbours


def backtrack(parent, end):
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = parent[current]
    return path[::-1]


def animate_move():
    sleep(SLEEP_TIME)
    redraw()


def redraw():
    draw_maze()
    pygame.display.flip()
    check_events()


def eukleid_distance(a, b):
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
            maze[current[::-1]] = 'c'
            animate_move()
            break

        for neighbour in get_neighbours(current):
            if neighbour not in visited:
                q.put(neighbour)
                visited.add(neighbour)
                parent[neighbour] = current

                maze[neighbour[::-1]] = 'o'
                animate_move()

        maze[current[::-1]] = 'c'
        animate_move()

    return backtrack(parent, end)


# A*  ------------------------------------------------------------------------------------------------------------------
def a_star(start, end, heuristic=eukleid_distance):
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
        cur_prio, current = q.get()

        if current == end:
            maze[current[::-1]] = 'c'
            animate_move()
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

        maze[current[::-1]] = 'c'
        animate_move()

    return backtrack(parent, end)


# Greedy ---------------------------------------------------------------------------------------------------------------
def greedy_search(start, end, heuristic=eukleid_distance):
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

        maze[current[::-1]] = 'c'
        animate_move()

    return backtrack(parent, end)


# RandomSearch ---------------------------------------------------------------------------------------------------------

def random_search(start, end):
    q = list()
    visited = set()
    parent = {}

    # init
    q.append(start)
    parent[start] = None
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
                animate_move()

        maze[current[::-1]] = 'c'
        animate_move()

    return backtrack(parent, end)


# DFS ------------------------------------------------------------------------------------------------------------------

def dfs_recursive(current, end, visited, parent):
    if current == end:
        return True

    visited.add(current)

    for neighbour in get_neighbours(current):
        if neighbour not in visited:
            parent[neighbour] = current

            maze[neighbour[::-1]] = 'o'
            animate_move()

            if dfs_recursive(neighbour, end, visited, parent):
                return True

    maze[current[::-1]] = 'c'
    animate_move()
    return False


def dfs(start, end):
    visited = set()
    parent = {start: None}

    dfs_recursive(start, end, visited, parent)
    return backtrack(parent, end)


def screen_init(start, end):
    global screen
    cols, rows = len(maze[0]), len(maze)
    screen_width, screen_height = cols * CELL_SIZE, rows * CELL_SIZE
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Maze")

    maze[start[::-1]] = 's'
    maze[end[::-1]] = 'e'
    animate_move()


def main():
    pygame.init()
    algorithms = {'bfs': bfs, 'dfs': dfs, 'a*': a_star, 'greedy': greedy_search, 'random': random_search}

    try:
        filename, algo = read_args()
        start, end = read_input(filename)
        screen_init(start, end)
        path = algorithms[algo](start, end)
        visualize_path(path, start, end)

    except Exception as e:
        print(e)
        return

    # Main loop
    while True:
        check_events()
        redraw()


if __name__ == "__main__":
    main()
