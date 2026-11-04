# n_puzzle: an Exact (Python) model from DCP Rosetta.
# Download the `n_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/n_puzzle.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python n_puzzle.py n_puzzle.json

from exact import Exact


def create_model(instance):
    """N-puzzle: on a square grid with tiles 1..n and one empty square (0), find the
    N_STEPS board states from the start state to the end state, where each state
    follows from the previous one by sliding a tile into the empty square. The board
    must change at every step."""
    n_steps = instance["N_STEPS"]     # the number of boards, counting the start and the end board
    start = instance["puzzle_start"]  # start[i][j]: the tile in row i, column j at the start
    end = instance["puzzle_end"]      # end[i][j]: the tile in row i, column j at the end
    dim = len(start)                  # the board is dim x dim squares
    squares = [(i, j) for i in range(dim) for j in range(dim)]  # the squares of the board
    tiles = range(dim * dim)          # 0 is the empty square, 1..dim*dim-1 are the tiles

    def neighbours(i, j):
        """The squares next to (i, j), to the left, right, above and below, inside the board."""
        return [(i + a, j + b) for a, b in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                if 0 <= i + a < dim and 0 <= j + b < dim]

    solver = Exact()

    # Exact identifies its variables by name.
    # holds[t][i][j][v] is 1 when square (i, j) holds tile v at step t, and 0 when not.
    # The start board fixes the tiles at the first step, and the end board at the last step.
    holds = [[[[f"holds_{t}_{i}_{j}_{v}" for v in tiles] for j in range(dim)]
              for i in range(dim)] for t in range(n_steps)]
    # steps[t][i][j] is the tile on square (i, j) at step t
    steps = [[[f"steps_{t}_{i}_{j}" for j in range(dim)] for i in range(dim)]
             for t in range(n_steps)]
    for t in range(n_steps):
        for i, j in squares:
            solver.addVariable(steps[t][i][j], 0, dim * dim - 1)
            for v in tiles:
                fixed = (t == 0 and start[i][j] == v) or (t == n_steps - 1 and end[i][j] == v)
                solver.addVariable(holds[t][i][j][v], 1 if fixed else 0, 1)

    for t in range(n_steps):
        # Each square holds exactly one tile at each step, and steps gives that tile.
        for i, j in squares:
            solver.addConstraint([(1, holds[t][i][j][v]) for v in tiles], True, 1, True, 1)
            solver.addConstraint([(v, holds[t][i][j][v]) for v in tiles if v]
                                 + [(-1, steps[t][i][j])], True, 0, True, 0)
        # Each tile is on exactly one square at each step.
        for v in tiles:
            solver.addConstraint([(1, holds[t][i][j][v]) for i, j in squares], True, 1, True, 1)

    for t in range(n_steps - 1):
        # The empty square moves to a neighbouring square at every step, so one tile slides into it.
        for i, j in squares:
            # The empty square is on (i, j) after the step only if it was next to (i, j) before.
            solver.addConstraint([(1, holds[t][ni][nj][0]) for ni, nj in neighbours(i, j)]
                                 + [(-1, holds[t + 1][i][j][0])], True, 0)
        # A square that is not empty before or after the step keeps its tile.
        for i, j in squares:
            for v in tiles:
                if v:
                    solver.addConstraint([(1, holds[t][i][j][v]), (-1, holds[t + 1][i][j][v]),
                                          (1, holds[t][i][j][0]), (1, holds[t + 1][i][j][0])], True, 0)
                    solver.addConstraint([(-1, holds[t][i][j][v]), (1, holds[t + 1][i][j][v]),
                                          (1, holds[t][i][j][0]), (1, holds[t + 1][i][j][0])], True, 0)

    return solver, {"steps": steps}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
