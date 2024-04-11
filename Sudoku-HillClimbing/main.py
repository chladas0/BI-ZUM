import random
from time import sleep

basic_sudoku = [
    [0, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 2, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 7],
    [0, 0, 4, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 5, 0, 6, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0]]

solved_sudoku = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9]]

real_sudoku1 = [
    [5, 0, 0, 0, 2, 0, 0, 6, 3],
    [0, 2, 0, 0, 0, 1, 0, 9, 0],
    [7, 0, 1, 8, 0, 0, 0, 0, 0],
    [3, 6, 0, 0, 0, 5, 9, 0, 0],
    [0, 0, 0, 9, 0, 7, 4, 0, 0],
    [8, 4, 0, 0, 1, 0, 0, 0, 2],
    [9, 0, 0, 0, 0, 6, 0, 2, 4],
    [0, 0, 0, 5, 3, 0, 0, 1, 0],
    [0, 8, 6, 0, 0, 0, 0, 0, 7]
]


class SudokuSolver:
    def __init__(self, sudoku):
        self.sudoku = sudoku
        self.fixed = set()
        self.not_fixed = set()
        self.not_fixed_vec = []

    # Visualizations ---------------------------------------------------------------------------------------------------
    # print the sudoku
    def print_sudoku(self):
        for i in range(9):
            for j in range(9):
                if self.sudoku[i][j] == 0:
                    print(" ", end=" ")
                else:
                    print(self.sudoku[i][j], end=" ")
                if j == 2 or j == 5:
                    print("|", end=" ")
            print()
            if i == 2 or i == 5:
                print("---------------------")

    # print the occurrences of each number in the sudoku
    def print_occurrences(self):
        for i in range(9):
            count = 0
            for j in range(9):
                for k in range(9):
                    if self.sudoku[j][k] == i + 1:
                        count += 1
            print(i, " : ", count)

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
            x1, x2 = random.randint(0, 8), random.randint(0, 8)
            y1, y2 = random.randint(0, 8), random.randint(0, 8)

            if (x1, y1) in self.fixed or (x2, y2) in self.fixed:
                continue

            self.swap_two_positions((x1, y1), (x2, y2))
            break

    # Hill Climbing Algorithm ------------------------------------------------------------------------------------------

    # hill climbing that is not choosing always the best choice
    # for each position it calculates its duplicates - row, col, block
    # if it is higher than 1 position is add to the array
    # then we choose random position from the array and search for the
    # position to be swapped, if the improvement is better than 1, we add
    # it to the array, in the end we choose random position from that second array
    # and swap those 2 positions
    def hill_climb_1(self):
        no_improvement = 0
        current_obj = self.objective_function()
        best_obj = current_obj

        while True:
            to_swap1, to_swap2 = [], []

            if current_obj == 0:
                print("The Sudoku was Solved", current_obj)
                self.print_sudoku()
                # maybe add visualization
                break

            # find the position with the highest value of the obj fun
            for i in range(9):
                for j in range(9):
                    if (i, j) not in self.fixed:
                        val = self.get_objective_val_for_position(i, j)
                        if val > 0:
                            to_swap1.append((i, j))

            first_pos = random.choice(to_swap1)

            # find the value that when swapped with val from previous cycle gives improvement > 0
            for i in range(9):
                for j in range(9):
                    if (i, j) not in self.fixed and (i, j) != first_pos:
                        improvement = self.getImprovement(first_pos, (i, j), current_obj)
                        if improvement > 0:
                            to_swap2.append((i, j))

            # found 2 positions to swap
            if to_swap2:
                self.swap_two_positions(first_pos, random.choice(to_swap2))
                no_improvement = 0
                current_obj = self.objective_function()

                if current_obj < best_obj:
                    best_obj = current_obj
                    print("Best objective function value: ", best_obj)

            else:
                no_improvement += 1
                if no_improvement > 5:
                    no_improvement = 0
                    self.shuffle_sudoku()
                    current_obj = self.objective_function()


def count_duplicates(arr):
    counter = {}
    for num in arr:
        counter[num] = counter[num] + 1 if num in counter else 1

    return sum(count - 1 for count in counter.values() if count > 1)


def main():
    solver = SudokuSolver(basic_sudoku)
    solver.fill_sudoku()
    solver.print_sudoku()
    solver.hill_climb_1()


if __name__ == '__main__':
    main()
