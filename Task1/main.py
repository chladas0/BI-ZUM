import random
from time import sleep
import pygame
import sys
from queue import Queue, PriorityQueue
import numpy as np

# todo calculate from rows and cols
CELL_SIZE = 10
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


# Visualization --------------------------------------------------------------------------------------------------------
def draw_maze(screen, maze):
    for y in range(len(maze)):
        for x in range(len(maze[y])):
            color = COLORS[maze[y][x]]
            pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def visualize_path(bfs_path, maze, screen, start, end):
    # Show start and end
    maze[start[::-1]] = 's'
    maze[end[::-1]] = 'e'

    animate_move(maze, screen)
    for vertex in bfs_path:
        maze[vertex[::-1]] = 'p'
        animate_move(maze, screen)


# Pygame - Check Events
def check_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


# Reading input --------------------------------------------------------------------------------------------------------
def read_input(filename):
    maze = []
    start, end = None, None
    with open(filename, 'r') as file:
        for line in file:
            row = line.strip()
            if "start" in row:
                start = tuple(map(int, row.replace("start", "").split(", ")))
            elif "end" in row:
                end = tuple(map(int, row.replace("end", "").split(", ")))
            else:
                maze.append(list(row))
    return np.array(maze), start, end


# Helper functions -----------------------------------------------------------------------------------------------------
def valid_position(maze, x, y, visited):
    return 0 <= x < len(maze[0]) and 0 <= y < len(maze) and maze[y][x] != 'X' and (x, y) not in visited


def get_neighbours(maze, current, visited):
    neighbours = []
    for neighbour in NEIGHBOURS:
        x = current[0] + neighbour[0]
        y = current[1] + neighbour[1]
        if valid_position(maze, x, y, visited):
            neighbours.append((x, y))
    return neighbours


def backtrack(parent, end):
    path = []
    current = end
    while current is not None:
        print(current)
        path.append(current)
        current = parent[current]
    return path[::-1]


def animate_move(maze, screen):
    #    sleep(SLEEP_TIME)
    redraw(screen, maze)


def redraw(screen, maze, clock=pygame.time.Clock()):
    draw_maze(screen, maze)
    pygame.display.flip()
    check_events()


def eukleid_distance(a, b):
    return np.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


# BFS ------------------------------------------------------------------------------------------------------------------
def bfs(maze, start, end, screen):
    q = Queue()
    visited = set()
    parent = {}

    # init
    q.put(start)
    parent[start] = None
    visited.add(start)

    while not q.empty():
        current = q.get()

        if current == end:
            maze[current[::-1]] = 'c'
            animate_move(maze, screen)
            break

        for neighbour in get_neighbours(maze, current, visited):
            if neighbour not in visited:
                q.put(neighbour)
                visited.add(neighbour)
                parent[neighbour] = current

                maze[neighbour[::-1]] = 'o'
                animate_move(maze, screen)

        maze[current[::-1]] = 'c'
        animate_move(maze, screen)

    return backtrack(parent, end)


# A*  ------------------------------------------------------------------------------------------------------------------


# TODO FIX STATES - CLOSED, OPEN, FRESH
def a_star(maze, start, end, screen, heuristic):
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
            animate_move(maze, screen)
            break

        for neighbour in get_neighbours(maze, current, visited):
            if neighbour not in visited:
                distance = dist[current] + 1
                dist[neighbour] = distance
                # + 1 for the cost of moving to the neighbour
                q.put((distance + heuristic(neighbour, end), neighbour))
                visited.add(neighbour)
                parent[neighbour] = current
                maze[neighbour[::-1]] = 'o'

        maze[current[::-1]] = 'c'
        animate_move(maze, screen)

    return backtrack(parent, end)


# Greedy ---------------------------------------------------------------------------------------------------------------
def greedy_search(maze, start, end, screen, heuristic):
    q = PriorityQueue()
    visited = set()
    parent = {}

    # init
    q.put((0, start))
    parent[start] = None
    visited.add(start)

    while not q.empty():
        cur_prio, current = q.get()

        if current == end:
            maze[current[::-1]] = 'c'
            animate_move(maze, screen)
            break

        for neighbour in get_neighbours(maze, current, visited):
            if neighbour not in visited:
                q.put((heuristic(neighbour, end), neighbour))
                visited.add(neighbour)
                parent[neighbour] = current
                maze[neighbour[::-1]] = 'o'

        maze[current[::-1]] = 'c'
        animate_move(maze, screen)

    return backtrack(parent, end)


# RandomSearch ---------------------------------------------------------------------------------------------------------

def random_search(maze, start, end, screen):
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
            maze[current[::-1]] = 'c'
            animate_move(maze, screen)
            break

        for neighbour in get_neighbours(maze, current, visited):
            if neighbour not in visited:
                q.append(neighbour)
                visited.add(neighbour)
                parent[neighbour] = current

                maze[neighbour[::-1]] = 'o'
                animate_move(maze, screen)

        maze[current[::-1]] = 'c'
        animate_move(maze, screen)

    return backtrack(parent, end)


# DFS

def dfs_recursive(maze, current, end, visited, parent, screen):
    if current == end:
        maze[current[::-1]] = 'c'
        animate_move(maze, screen)
        return True

    visited.add(current)

    for neighbour in get_neighbours(maze, current, visited):
        if neighbour not in visited:
            parent[neighbour] = current

            maze[neighbour[::-1]] = 'o'
            animate_move(maze, screen)

            if dfs_recursive(maze, neighbour, end, visited, parent, screen):
                return True

    maze[current[::-1]] = 'c'
    animate_move(maze, screen)
    return False

def dfs(maze, start, end, screen):
    visited = set()
    parent = {}

    # Initialize
    parent[start] = None

    dfs_recursive(maze, start, end, visited, parent, screen)
    return backtrack(parent, end)

def main():
    pygame.init()

    # TODO read filename from cmdline
    filename = "dataset/6.txt"

    maze, start, end = read_input(filename)
    cols, rows = len(maze[0]), len(maze)

    maze_copy = maze.copy()

    # Set up the screen
    screen_width, screen_height = cols * CELL_SIZE, rows * CELL_SIZE
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Maze")

    maze[start[::-1]] = 's'
    maze[end[::-1]] = 'e'

    redraw(screen, maze)
    sleep(SLEEP_TIME)

    # bfs_path = bfs(maze, start, end, screen)
    # sleep(SLEEP_TIME)
    # visualize_path(bfs_path, maze, screen, start, end)

    maze = maze_copy.copy()

#    A* with eukleid distance
    a_star_path = a_star(maze, start, end, screen, eukleid_distance)
    sleep(SLEEP_TIME)
    visualize_path(a_star_path, maze, screen, start, end)

    maze = maze_copy.copy()

#    Greedy with eukleid distance
    greedy_path = greedy_search(maze, start, end, screen, eukleid_distance)
    sleep(SLEEP_TIME)
    visualize_path(greedy_path, maze, screen, start, end)


    # Random search
    # maze = maze_copy.copy()
    # random_path = random_search(maze, start, end, screen)
    # sleep(SLEEP_TIME)
    # visualize_path(random_path, maze, screen, start, end)

    # DFS
    maze = maze_copy.copy()
    dfs_path = dfs(maze, start, end, screen)
    sleep(SLEEP_TIME)
    visualize_path(dfs_path, maze, screen, start, end)

    # Main loop
    while True:
        check_events()
        redraw(screen, maze)


if __name__ == "__main__":
    main()
