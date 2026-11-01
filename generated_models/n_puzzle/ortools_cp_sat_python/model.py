# n_puzzle: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `n_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/n_puzzle.html
# Then run it on the first instance (after `pip install ortools`):
#   python n_puzzle.py n_puzzle.json

from ortools.sat.python import cp_model


def create_model(instance):
    """N-puzzle: on a square grid with tiles 1..n and one empty square (0), find the
    N_STEPS board states from the start state to the end state, where each state
    follows from the previous one by sliding a tile into the empty square. The board
    must change at every step."""
    n_steps = instance["N_STEPS"]     # number of boards, counting the start and end boards
    start = instance["puzzle_start"]  # start[i][j]: the tile in row i, column j at the start
    end = instance["puzzle_end"]      # end[i][j]: the tile in row i, column j at the end
    dim = len(start)                  # the board is dim x dim squares
    n_tiles = dim * dim - 1           # the number of numbered tiles

    model = cp_model.CpModel()

    # steps[t][i][j]: the tile in row i, column j at step t (0 = empty square)
    steps = [[[model.new_int_var(0, n_tiles, f"steps_{t}_{i}_{j}")
               for j in range(dim)]
              for i in range(dim)]
             for t in range(n_steps)]

    # empty[t][i][j] is true when the empty square is at row i, column j at step t
    empty = [[[model.new_bool_var(f"empty_{t}_{i}_{j}")
               for j in range(dim)]
              for i in range(dim)]
             for t in range(n_steps)]

    # A square is empty exactly when its tile is 0.
    for t in range(n_steps):
        for i in range(dim):
            for j in range(dim):
                model.add(steps[t][i][j] == 0).only_enforce_if(empty[t][i][j])
                model.add(steps[t][i][j] != 0).only_enforce_if(~empty[t][i][j])

    # The first board is the start state and the last one is the end state.
    for i in range(dim):
        for j in range(dim):
            model.add(steps[0][i][j] == start[i][j])
            model.add(steps[n_steps - 1][i][j] == end[i][j])

    for t in range(1, n_steps):
        # before and after: the boards at the previous step and at this step
        before, after = steps[t - 1], steps[t]

        # Every board holds each tile exactly once.
        model.add_all_different([after[i][j] for i in range(dim) for j in range(dim)])

        # changed: the squares whose tile differs from the previous board
        changed = []
        for i in range(dim):
            for j in range(dim):
                # around: this square and the squares next to it, above, below, left and right
                around = [(i + a, j + b) for a, b in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]
                          if 0 <= i + a < dim and 0 <= j + b < dim]
                # The empty square moves to a neighbouring square or stays put: if it is here
                # now, it was on one of these squares before the move.
                model.add_bool_or([empty[t - 1][r][c] for r, c in around]).only_enforce_if(empty[t][i][j])

                # same: the square keeps its tile. Only the empty square moves, so a square
                # keeps its tile unless the empty square is on it before or after the move.
                same = model.new_bool_var(f"same_{t}_{i}_{j}")
                model.add(before[i][j] == after[i][j]).only_enforce_if(same)
                model.add(before[i][j] != after[i][j]).only_enforce_if(~same)
                model.add_bool_or([empty[t - 1][i][j], empty[t][i][j], same])
                changed.append(~same)

        # The board changes at every step: at least one square holds a different tile.
        model.add_bool_or(changed)

    return model, {"steps": steps}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
