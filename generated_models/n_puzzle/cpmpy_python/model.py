# n_puzzle: a CPMpy model from DCP Rosetta.
# Download the `n_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/n_puzzle.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python n_puzzle.py n_puzzle.json

import cpmpy as cp


def create_model(instance):
    """N-puzzle: on a square grid with tiles 1..n and one empty square (0), find the
    N_STEPS board states from the start state to the end state, where each state
    follows from the previous one by sliding a tile into the empty square. The board
    must change at every step."""
    n_steps = instance["N_STEPS"]      # number of states, counting the start and end states
    start = instance["puzzle_start"]   # start[i][j]: the tile in row i, column j at the start (0 = empty)
    end = instance["puzzle_end"]       # end[i][j]: the tile in row i, column j at the end (0 = empty)
    dim = len(start)
    n_tiles = dim * dim - 1            # the numbered tiles, e.g. 8 for the 3 x 3 puzzle

    # steps[t, i, j] is the tile in row i, column j at step t (0 = empty square)
    steps = cp.intvar(0, n_tiles, shape=(n_steps, dim, dim), name="steps")

    model = cp.Model()

    # The first state is the start state and the last state is the end state.
    model.add(steps[0] == start)
    model.add(steps[n_steps - 1] == end)

    for t in range(1, n_steps):
        before, after = steps[t - 1], steps[t]

        # Every state holds each tile exactly once.
        model.add(cp.AllDifferent(after))

        # The empty square ends up where it was or on a neighbouring square (left, right, above or below).
        for i in range(dim):
            for j in range(dim):
                nearby = [(i + a, j + b) for a, b in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]
                          if 0 <= i + a < dim and 0 <= j + b < dim]
                model.add((after[i, j] == 0).implies(cp.any([before[r, c] == 0 for r, c in nearby])))

        # Only the empty square moves: a square keeps its tile, unless the empty square
        # was there before or is there after.
        model.add((before == 0) | (after == 0) | (before == after))

        # The board changes at every step: no standing still.
        model.add(cp.any(before != after))

    return model, {"steps": steps}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
