# n_puzzle: a CPLEX (Python) model from DCP Rosetta.
# Download the `n_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/n_puzzle.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python n_puzzle.py n_puzzle.json

from docplex.mp.model import Model


def create_model(instance):
    """N-puzzle: on a square board of numbered tiles with one empty cell (0), find the sequence of
    N_STEPS board states from the start state to the end state in which every step slides one tile
    into the empty cell; the board has to change at every step."""
    n_steps = instance["N_STEPS"]          # number of board states, start and end included
    start = instance["puzzle_start"]  # board at the first step; 0 is the empty cell
    end = instance["puzzle_end"]      # board at the last step
    dim = len(start)
    cells = [(i, j) for i in range(dim) for j in range(dim)]
    tiles = range(dim * dim)          # 0 (empty) and the tiles 1..dim*dim-1
    max_tile = dim * dim - 1                 # largest tile number: the widest change of a cell

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def neighbours(cell):
        return [(cell[0] + a, cell[1] + b) for a, b in ((-1, 0), (1, 0), (0, -1), (0, 1))
                if 0 <= cell[0] + a < dim and 0 <= cell[1] + b < dim]

    # at_start[v] and at_end[v] are the cell holding tile v on the first and on the last board
    at_start = {start[i][j]: (i, j) for i, j in cells}
    at_end = {end[i][j]: (i, j) for i, j in cells}

    # Which tile can stand on which cell at which step. Every step slides exactly one tile one
    # cell, so the n_steps - 1 steps are shared by all tiles: tile v travels at least the distance
    # between its start and end cells, and at most that plus the slack the other tiles leave.
    # The empty cell moves at every step, so its distance from its start has the parity of the
    # step. These are consequences of the rules, not extra rules; they keep the one-hot
    # encoding below inside the Community Edition's 1000-variable limit (496 binaries on the
    # 4x4 instance instead of 13 * 16 * 16).
    least = sum(manhattan(at_start[v], at_end[v]) for v in tiles if v != 0)
    slack = (n_steps - 1) - least

    def possible(t, cell, v):
        if v not in at_start or v not in at_end:
            return False
        a, b = manhattan(at_start[v], cell), manhattan(cell, at_end[v])
        if a > t or b > n_steps - 1 - t:
            return False
        if v == 0:
            return (t - a) % 2 == 0
        return a + b <= manhattan(at_start[v], at_end[v]) + slack

    model = Model("n_puzzle")

    # holds[t, cell, v] = 1 when cell cell shows tile v at step t. The first and last boards are given.
    holds = {}
    for t in range(n_steps):
        for cell in cells:
            for v in tiles:
                if t == 0:
                    holds[t, cell, v] = 1 if start[cell[0]][cell[1]] == v else 0
                elif t == n_steps - 1:
                    holds[t, cell, v] = 1 if end[cell[0]][cell[1]] == v else 0
                elif possible(t, cell, v):
                    holds[t, cell, v] = model.binary_var(name=f"holds_{t}_{cell[0]}_{cell[1]}_{v}")

    def expr(items):
        e = model.linear_expr()
        for item in items:
            e += item
        return e

    def blank(t, cell):
        # 1 when cell shows the empty cell at step t, else 0 (a constant where the pruning rules it out)
        return expr([holds.get((t, cell, 0), 0)])

    # x[t][cell] is the tile on cell cell at step t.
    x = {(t, cell): expr([v * holds[t, cell, v] for v in tiles if (t, cell, v) in holds])
         for t in range(n_steps) for cell in cells}

    impossible = []

    def post(left, sense, right):
        # A relation between constants is checked here: docplex needs a variable to post one.
        d = left - right
        if d.is_constant():
            k = d.constant
            if not ((sense == "<=" and k <= 0) or (sense == "==" and k == 0) or (sense == ">=" and k >= 0)):
                impossible.append(True)
            return
        if sense == "<=":
            model.add_constraint(left <= right)
        elif sense == ">=":
            model.add_constraint(left >= right)
        else:
            model.add_constraint(left == right)

    for t in range(1, n_steps - 1):
        # Every cell shows exactly one tile (or is the empty cell).
        for cell in cells:
            post(expr([holds[t, cell, v] for v in tiles if (t, cell, v) in holds]), "==", expr([1]))
        # There is exactly one empty cell.
        post(expr([blank(t, cell) for cell in cells]), "==", expr([1]))
        # Sliding never adds or removes a tile, so the tile numbers on the board keep their total.
        post(expr([x[t, cell] for cell in cells]), "==", expr([sum(tiles)]))

    for t in range(n_steps - 1):
        for cell in cells:
            # The empty cell moves to a neighbouring cell at every step: the board must change,
            # and only the tile next to the empty cell can slide into it.
            if (t + 1, cell, 0) in holds:
                post(blank(t + 1, cell), "<=", expr([blank(t, r) for r in neighbours(cell)]))
            # Only the tile sliding into the empty cell moves: a cell that is empty neither before
            # nor after the step keeps its tile. Together with the constant total above, the cell
            # the empty space leaves receives exactly the tile that slid, so every board holds
            # each tile once.
            changing = blank(t, cell) + blank(t + 1, cell)
            if changing.is_constant() and changing.constant == 0:
                post(x[t + 1, cell], "==", x[t, cell])
            else:
                post(x[t + 1, cell] - x[t, cell], "<=", max_tile * changing)
                post(x[t, cell] - x[t + 1, cell], "<=", max_tile * changing)

    if impossible:
        # The given start and end cannot be joined in N_STEPS boards.
        flag = model.binary_var(name="impossible")
        model.add_constraint(flag == 1)
        model.add_constraint(flag == 0)

    steps = []
    for t in range(n_steps):
        board = []
        for i in range(dim):
            row = []
            for j in range(dim):
                e = x[t, (i, j)]
                row.append(int(e.constant) if e.is_constant() else e)
            board.append(row)
        steps.append(board)
    return model, {"steps": steps}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
