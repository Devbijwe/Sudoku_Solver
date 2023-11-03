from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.secret_key = 'supersecretkey'

class CSP:
    def __init__(self, size,puzzle):
        self.size = size
        self.subgrid_size = int(size**0.5)
        self.variables = [(i, j) for i in range(size) for j in range(size)]
        self.domains = {var: set(range(1, 10)) if puzzle[var[0]][var[1]] == 0 else {puzzle[var[0]][var[1]]} for var in self.variables}

        self.constraints = {}
        # self.solution=None
        # print("var",self.variables)
        # print("dom",self.domains)
        for var in self.variables:
            self.constraints[var] = self.get_all_constraints(var)
        # print("constraints:",self.constraints)
    def get_all_constraints(self, var):
        constraints = []
        for i in range(self.size):
            if i != var[0]:
                constraints.append((i, var[1]))
            if i != var[1]:
                constraints.append((var[0], i))

        subgrid_row = var[0] // self.subgrid_size
        subgrid_col = var[1] // self.subgrid_size
        
        for i in range(self.subgrid_size * subgrid_row, self.subgrid_size * (subgrid_row + 1)):
            for j in range(self.subgrid_size * subgrid_col, self.subgrid_size * (subgrid_col + 1)):
                if (i, j) != var:
                    constraints.append((i, j))
        
        return constraints
        
        
        

    # Rest of the CSP class remains the same

    def solve(self):
        assignment = {}
        self.solution = self.backtrack(assignment)
        return self.solution

    def backtrack(self, assignment):
        # print(len(assignment),len(self.variables))
        if len(assignment) == len(self.variables):
            # print(assignment)
            return assignment

        var = self.select_unassigned_variable(assignment)
        # print("var:",var)
        for value in self.order_domain_values(var, assignment):
            if self.is_consistent(var, value, assignment):
                assignment[var] = value
                result = self.backtrack(assignment)
                if result is not None:
                    return result
                del assignment[var]
        return None

    def select_unassigned_variable(self, assignment):
        unassigned_vars = [var for var in self.variables if var not in assignment]
        return min(unassigned_vars, key=lambda var: len(self.domains[var]))

    def order_domain_values(self, var, assignment):
        return self.domains[var]

    def is_consistent(self, var, value, assignment):
        for constraint_var in self.constraints[var]:
            if constraint_var in assignment and assignment[constraint_var] == value:
                return False
        return True

def convert_solution_to_list(solution, size):
    board = [[0] * size for _ in range(size)]
    for var, value in solution.items():
        i, j = var
        board[i][j] = value
    return board

@app.route('/')
def home():
    selected_size = int(request.args.get("selected_size", 9))
    selected_size = max(3, min(selected_size, 36))

    # Define the size options
    size_options = [4, 9, 16, 25, 36]  # Add more size options as needed
    # selected_size = size  # The selected size will be the current 'size'
    
    return render_template('index.html', size_options=size_options, selected_size=selected_size)

@app.route('/solve-sudoku', methods=['POST'])
def solve_sudoku_route():
    if request.method == 'POST':
        try:
            data = request.get_json()
            puzzle = data.get('puzzle')
            
            # Convert the puzzle to integers
            puzzle = [[int(cell) for cell in row] for row in puzzle]
            print(puzzle)
        #     puzzle = [[5, 3, 0, 0, 7, 0, 0, 0, 0], 
		# [6, 0, 0, 1, 9, 5, 0, 0, 0], 
		# [0, 9, 8, 0, 0, 0, 0, 6, 0], 
		# [8, 0, 0, 0, 6, 0, 0, 0, 3], 
		# [4, 0, 0, 8, 0, 3, 0, 0, 1], 
		# [7, 0, 0, 0, 2, 0, 0, 0, 6], 
		# [0, 6, 0, 0, 0, 0, 2, 8, 0], 
		# [0, 0, 0, 4, 1, 9, 0, 0, 5], 
		# [0, 0, 0, 0, 8, 0, 0, 0, 0] 
		# ] 
            size = len(puzzle)
            csp = CSP(size,puzzle)
            
            
            # Call your Sudoku solving function
            solution = csp.solve()
            
            # print(solution)
            if solution:
                solution_list = convert_solution_to_list(solution, size)
                return jsonify({'solution': solution_list})
            else:
                return jsonify({'error': 'No solution found'})
        except Exception as e:
            return jsonify({'error': str(e)})

