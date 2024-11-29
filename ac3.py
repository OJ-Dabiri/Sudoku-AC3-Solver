from collections import defaultdict, deque




class SudokuCSP:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.domains = self.initialize_domains()
        self.neighbors = self.initialize_neighbors()


    def initialize_domains(self):
        # Each cell (i, j) has a domain of values (1-9) if unassigned, or the assigned value in the puzzle
        domains = {}
        for i in range(9):
            for j in range(9):
                if self.puzzle[i][j] == 0:
                    domains[(i, j)] = set(range(1, 10))
                else:
                    domains[(i, j)] = {self.puzzle[i][j]}
        return domains


    def initialize_neighbors(self):
        # Initialize neighbors for each cell
        neighbors = defaultdict(set)
        for i in range(9):
            for j in range(9):
                # Get Row and column constraints
                for k in range(9):
                    if k != j:
                        neighbors[(i, j)].add((i, k))
                    if k != i:
                        neighbors[(i, j)].add((k, j))
                # Sub-grid constraints
                start_row, start_col = 3 * (i // 3), 3 * (j // 3)
                for r in range(start_row, start_row + 3):
                    for c in range(start_col, start_col + 3):
                        if (r, c) != (i, j):
                            neighbors[(i, j)].add((r, c))
        return neighbors


    def ac3(self):
        queue = deque([(xi, xj) for xi in self.domains for xj in self.neighbors[xi]])
        queue_lengths = []  # To store the length of the queue at end of each step in ac3 algorithm

        while queue:

            queue_lengths.append(len(queue))

            (xi, xj) = queue.popleft()
            if self.revise(xi, xj):
                if not self.domains[xi]:
                    print("Puzzle has no solution")
                    return False, queue_lengths  # Return failure if any domain is empty, means no soluiton
                
                for xk in self.neighbors[xi] - {xj}:
                    queue.append((xk, xi))
        return True, queue_lengths


    def revise(self, xi, xj):
        revised = False
        for x in set(self.domains[xi]):  # Use set to avoid modifying the domain during iteration of variables
            if not any(self.constraint_satisfied(x, y) for y in self.domains[xj]):
                self.domains[xi].remove(x)
                revised = True
        return revised


    def constraint_satisfied(self, x, y):
        return x != y


    def is_solved(self):
        return all(len(domain) == 1 for domain in self.domains.values())


    def get_solution(self):
        return [[next(iter(self.domains[(i, j)])) for j in range(9)] for i in range(9)]




    def select_unassigned_variable(self, assignment):
        # Choose an unassigned variable with the fewest legal values (MRV heuristic)
        unassigned_variables = [v for v in self.domains if v not in assignment]
        return min(unassigned_variables, key=lambda var: len(self.domains[var]))


    def is_consistent(self, var, value, assignment):
        # Check if assigning value to var conflicts with neighboring variables
        for neighbor in self.neighbors[var]:
            if neighbor in assignment and assignment[neighbor] == value:
                return False
        return True
    
    def least_constraining_values(self, var, assignment):
        # Least Constraining Value Heuristic
        # count the number of eliminated possibilities for each possible value for the variable
        values = list(self.domains[var])
        values.sort(key=lambda value: self.count_constraints(var, value, assignment))
        return values

    def count_constraints(self, var, value, assignment):
        # Count how many values in the neighboring domains would be eliminated
        count = 0
        for neighbor in self.neighbors[var]:
            if neighbor not in assignment:
                count += sum(1 for neighbor_value in self.domains[neighbor] if not self.constraint_satisfied(value, neighbor_value))
        return count
    
    def backtracking_search(self):
        return self.backtrack({})

    def backtrack(self, assignment):
        if len(assignment) == 81:  # Assign all variables
            return assignment
        
        var = self.select_unassigned_variable(assignment)

        for value in self.least_constraining_values(var, assignment):
            if self.is_consistent(var, value, assignment):
                assignment[var] = value
                result = self.backtrack(assignment)

                if result is not None:
                    return result
                
                del assignment[var]
        return None


#Solve puzzle functiion
def solve_sudoku(puzzle):
    csp = SudokuCSP(puzzle)
    ac3_result, queue_lengths = csp.ac3()
    if ac3_result:
        if csp.is_solved():
            #Sudoku finished by AC3 algorithm
            print("Sudoku fully solved by CSP....Printing queue lengths at each step of the AC-3 Algorithm in an array")
            return csp.get_solution(), queue_lengths
        else:
            print("Sudoku not fully solved by CSP....Running Backtrack algorithm")
            solution = csp.backtracking_search()
            if solution:
                solved_puzzle = [[solution.get((i, j), 0) for j in range(9)] for i in range(9)]
                return solved_puzzle, queue_lengths
    return None, queue_lengths


# Sample 9x9 Sudoku puzzle input (0 represents empty cells)
puzzle = [
    [0, 0, 0, 0, 0, 0, 2, 0, 0],
    [0, 0, 0, 6, 0, 0, 0, 0, 3],
    [0, 7, 4, 0, 8, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 3, 0, 0, 2],
    [0, 8, 0, 0, 4, 0, 0, 1, 0],
    [6, 0, 0, 5, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 7, 8, 0],
    [5, 0, 0, 0, 0, 9, 0, 0, 0],
    [0, 0, 8, 0, 0, 0, 0, 0, 0]
]

puzzle5 = [
    [8, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 3, 6, 0, 0, 0, 0, 0],
    [0, 7, 0, 0, 9, 0, 2, 0, 0],
    [0, 5, 0, 0, 0, 7, 0, 0, 0],
    [0, 0, 0, 0, 4, 5, 7, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 3, 0],
    [0, 0, 1, 0, 0, 0, 0, 6, 8],
    [0, 0, 8, 5, 0, 0, 0, 1, 0],
    [0, 9, 0, 0, 0, 0, 4, 0, 0]
]

puzzle_backtrack = [
    [0, 0, 0, 0, 0, 0, 2, 0, 0],
    [0, 0, 0, 6, 0, 0, 0, 0, 3],
    [0, 7, 4, 0, 8, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 3, 0, 0, 2],
    [0, 8, 0, 0, 4, 0, 0, 1, 0],
    [6, 0, 0, 5, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [5, 0, 0, 0, 0, 9, 0, 0, 0],
    [0, 0, 8, 0, 0, 0, 0, 0, 0]
]

puzzle_no_solution = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 0, 5, 6, 7],
    [8, 5, 9, 7, 6, 2, 4, 0, 3],  # Empty cell in row 4, column 8
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9]
]

puzzle_ac3_solution = [
    [5, 1, 7, 6, 0, 0, 0, 3, 4],
    [2, 8, 9, 0, 0, 4, 0, 0, 0],
    [3, 4, 6, 2, 0, 5, 0, 9, 0],
    [6, 0, 2, 0, 0, 0, 0, 1, 0],
    [0, 3, 8, 0, 0, 6, 0, 4, 7],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 9, 0, 0, 0, 0, 0, 7, 8],
    [7, 0, 3, 4, 0, 0, 5, 6, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0]
]


solution, queue_lengths = solve_sudoku(puzzle5)

print("Total number of steps taken for AC-3 algorithm: "+str(len(queue_lengths)))
print("\n"+"Queue Lengths at Each Step of AC-3:", queue_lengths)
if solution:
    print("Solved Puzzle:")
    for row in solution:
        print(row)
else:
    print("No solution found.")
