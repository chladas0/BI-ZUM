import copy
import random
from time import sleep

import pygame.display

from constants import *
from vizualization import *


class SudokuSolver:
    def __init__(self, sudoku):
        self.given_sudoku = copy.deepcopy(sudoku)
        self.sudoku = sudoku
        self.fixed = set()
        self.not_fixed = set()
        self.not_fixed_vec = []
        self.fill_sudoku()
        self.screen = init_screen()

    # Visualizations ---------------------------------------------------------------------------------------------------
    def redraw(self):
        self.screen.fill((255, 255, 255))
        visualize_sudoku(self.screen, self.given_sudoku, 50, 50)
        visualize_sudoku(self.screen, self.sudoku, 1000, 50, solved=True)
        pygame.display.flip()

    # Reading and filling the sudoku -----------------------------------------------------------------------------------
    def fill_sudoku(self):
        to_fill = self.get_unused_values()
        random.shuffle(to_fill)

        for i in range(9):
            for j in range(9):
                if self.sudoku[i][j] == 0:
                    self.sudoku[i][j] = to_fill.pop()

    # get all values that are not used in the sudoku (9 times {1..9})
    def get_unused_values(self):
        to_fill = []
        used_values = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}

        for i in range(9):
            for j in range(9):
                if self.sudoku[i][j] != 0:
                    self.fixed.add((i, j))
                    used_values[self.sudoku[i][j]] += 1
                else:
                    self.not_fixed.add((i, j))
                    self.not_fixed_vec.append((i, j))

        for i in range(9):
            for val, amount in used_values.items():
                if amount != 9:
                    to_fill.append(val)
                    used_values[val] += 1

        return to_fill

    # Helper Function for the Hill Climbing Algorithm ------------------------------------------------------------------
    def objective_function(self):
        violation = 0

        # count violations in row
        for row in self.sudoku:
            violation += count_duplicates(row)

        # count violations in blocks
        for i in range(3):
            for j in range(3):
                block = [self.sudoku[row][col] for row in range(i * 3, (i + 1) * 3) for col in
                         range(j * 3, (j + 1) * 3)]
                violation += count_duplicates(block)

        # count violations in column
        for col_index in range(len(self.sudoku[0])):
            column = [row[col_index] for row in self.sudoku]
            violation += count_duplicates(column)

        return violation

    # add up duplicates of the value at row, col and block
    def get_objective_val_for_position(self, row, col):
        count = 0
        val = self.sudoku[row][col]

        # duplicates of val
        for i in range(9):
            if i != col and self.sudoku[row][i] == val:
                count += 1

        # column
        for i in range(9):
            if i != row and self.sudoku[i][col] == val:
                count += 1

        # block
        block_row, block_col = row // 3, col // 3
        for i in range(3):
            for j in range(3):
                if (i != row % 3 or j != col % 3) and self.sudoku[block_row * 3 + i][block_col * 3 + j] == val:
                    count += 1

        return count

    # Swaps the values at p1 and p2
    def swap_two_positions(self, p1, p2):
        self.sudoku[p1[0]][p1[1]], self.sudoku[p2[0]][p2[1]] = self.sudoku[p2[0]][p2[1]], self.sudoku[p1[0]][p1[1]]

    # Returns the improvement of the objective function when swapping the values at p1 and p2
    def getImprovement(self, p1, p2, current_obj):
        # swap the values at positions p1 and p2
        self.swap_two_positions(p1, p2)

        # check the new value of the objective function
        new_val = self.objective_function()

        # swap back
        self.swap_two_positions(p1, p2)

        return current_obj - new_val

    # chooses 2 random positions that are not fixed and swaps them
    def shuffle_sudoku(self):

        while True:
            # get random int 0 to 9 not including
            pos1 = random.choice(self.not_fixed_vec)
            pos2 = random.choice(self.not_fixed_vec)

            self.swap_two_positions(pos1, pos2)
            break

    # Hill Climbing Algorithms -----------------------------------------------------------------------------------------
    def hill_climbing_classic(self):
        no_improvement, current_obj_val, best_obj_val = 0, self.objective_function(), self.objective_function()
        hard_reset = 0

        while current_obj_val != 0:
            to_swap1, to_swap2, best_val, best_improvement = [], [], None, None

            for i, j in self.not_fixed_vec:
                val = self.get_objective_val_for_position(i, j)
                if not to_swap1 or val > best_val:
                    to_swap1 = [(i, j)]
                    best_val = val
                elif val == best_val:
                    to_swap1.append((i, j))

            first_pos = random.choice(to_swap1)

            # the position with the highest obj val is stored in to_swap1
            # now find the position that swapped with to_swap1 gives the best improvement

            for i, j in self.not_fixed_vec:
                improvement = self.getImprovement(first_pos, (i, j), current_obj_val)
                if not to_swap2 or improvement > best_improvement:
                    to_swap2 = [(i, j)]
                    best_improvement = improvement
                elif improvement == best_improvement:
                    to_swap2.append((i, j))

            # Swap the best found and check improving
            self.swap_two_positions(first_pos, random.choice(to_swap2))
            current_obj_val = self.objective_function()

            if current_obj_val < best_obj_val:
                best_obj_val = current_obj_val

            if best_improvement <= 0:
                no_improvement += 1
            else:
                no_improvement = 0

            if no_improvement > 5:
                hard_reset += 1
                no_improvement = 0
                self.shuffle_sudoku()
                current_obj_val = self.objective_function()

            # if 10 soft resets didn't help shuffle more
            if hard_reset > 10:
                hard_reset = 0
                for i in range(20):
                    self.shuffle_sudoku()

            self.redraw()

    # hill climbing that is not choosing always the best choice
    # for each position it calculates its duplicates - row, col, block
    # if it is higher than 1 position is add to the array
    # then we choose random position from the array and search for the
    # position to be swapped, if the improvement is better than 1, we add
    # it to the array, in the end we choose random position from that second array
    # and swap those 2 positions
    def hill_climb_randomized(self):
        no_improvement, current_obj_val, best_obj_val = 0, self.objective_function(), self.objective_function()
        hard_reset = 0

        while current_obj_val != 0:
            to_swap1, to_swap2 = [], []

            # Collect all the position with objective_val > 1 (at least one duplicate row, col or block)
            for i, j in self.not_fixed_vec:
                val = self.get_objective_val_for_position(i, j)
                if val > 0:
                    to_swap1.append((i, j))

            first_pos = random.choice(to_swap1)
            # find the value that when swapped with val from previous cycle gives some improvement
            for i, j in self.not_fixed_vec:
                if (i, j) != first_pos:
                    improvement = self.getImprovement(first_pos, (i, j), current_obj_val)
                    if improvement > 0:
                        to_swap2.append((i, j))

            # found 2 positions to swap
            if to_swap2:
                second_pos = random.choice(to_swap2)
                self.swap_two_positions(first_pos, second_pos)
                current_obj_val = self.objective_function()
                no_improvement = 0

                if current_obj_val < best_obj_val:
                    best_obj_val = current_obj_val

            else:
                no_improvement += 1
                if no_improvement > 5:
                    hard_reset += 1
                    no_improvement = 0
                    self.shuffle_sudoku()
                    current_obj_val = self.objective_function()

            if hard_reset > 10:
                hard_reset = 0
                for i in range(20):
                    self.shuffle_sudoku()

            self.redraw()


def count_duplicates(arr):
    counter = {}
    for num in arr:
        counter[num] = counter[num] + 1 if num in counter else 1

    return sum(count - 1 for count in counter.values() if count > 1)


def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <sudoku{1..4}> <hill_climbing_type{classic/random}>")
        exit(1)
    sudoku = None

    match sys.argv[1]:
        case "1":
            sudoku = sudoku1
        case "2":
            sudoku = sudoku2
        case "3":
            sudoku = hard_sudoku
        case "4":
            sudoku = solved_sudoku

    solver = SudokuSolver(sudoku)

    match sys.argv[2]:
        case "classic":
            solver.hill_climbing_classic()
        case "random":
            solver.hill_climb_randomized()

    display_solved_message(solver.screen, 1000, 1400)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.flip()


if __name__ == '__main__':
    main()
