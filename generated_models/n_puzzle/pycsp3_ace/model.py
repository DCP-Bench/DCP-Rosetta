# n_puzzle: a PyCSP3 model from DCP Rosetta.
# Download the `n_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/n_puzzle.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python n_puzzle.py n_puzzle.json

from pycsp3 import *


def create_model(instance):
    """The N-Puzzle: a grid of tiles with one empty tile (0). Trace the steps from the start
    configuration to the end configuration, using exactly N_STEPS states including the start and
    the end. Each step moves one tile that is horizontally or vertically next to the empty tile
    into the empty position, and the state must change at each step."""
    n_steps = instance["N_STEPS"]            # the number of states, the start and the end included
    puzzle_start = instance["puzzle_start"]  # the start configuration; 0 is the empty tile
    puzzle_end = instance["puzzle_end"]      # the end configuration; 0 is the empty tile
    side = len(puzzle_start)                 # the grid is side x side
    n_cells = side * side                    # the cells are numbered 0 .. n_cells - 1, row by row; the tiles are 0 .. n_cells - 1

    # steps[t][r][c] is the tile on cell (r, c) in state t (0 is the empty tile).
    steps = VarArray(size=[n_steps, side, side], dom=range(n_cells))

    # blank[t] is the number of the cell holding the empty tile in state t.
    blank = VarArray(size=n_steps, dom=range(n_cells))

    # The tile on cell k (a cell number) in state t.
    def tile(t, k):
        r, c = divmod(k, side)
        return steps[t][r][c]

    # Pairs of cells (k, q) that share a side: the empty tile slides from k to q or back.
    neighbours = [
        (k, q)
        for k in range(n_cells)
        for q in range(n_cells)
        if abs(k // side - q // side) + abs(k % side - q % side) == 1
    ]

    satisfy(
        # The first state is the start configuration and the last state is the end configuration.
        [steps[0][r][c] == puzzle_start[r][c] for r in range(side) for c in range(side)],
        [steps[n_steps - 1][r][c] == puzzle_end[r][c] for r in range(side) for c in range(side)],
        # Every state holds each tile exactly once.
        [AllDifferent(steps[t]) for t in range(n_steps)],
        # The empty tile is in the cell that blank[t] names, in every state.
        [(tile(t, k) == 0) == (blank[t] == k) for t in range(n_steps) for k in range(n_cells)],
        # Each step moves the empty tile to a cell next to its previous one. The state then changes at each step,
        # since the empty tile moves; so freezing is excluded without a separate constraint.
        [Table(scope=[blank[t], blank[t + 1]], supports=neighbours) for t in range(n_steps - 1)],
        # A step moves the tile from the cell the empty tile enters into the cell it leaves.
        [Or(blank[t] != k, blank[t + 1] != q, tile(t + 1, k) == tile(t, q))
         for t in range(n_steps - 1) for k, q in neighbours],
        # Every other cell keeps its tile in a step.
        [Or(tile(t + 1, k) == tile(t, k), blank[t] == k, blank[t + 1] == k)
         for t in range(n_steps - 1) for k in range(n_cells)],
    )

    return {"steps": steps}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        print("steps", "=")
        for row in outputs["steps"]:
            print(values(row))
    else:
        print("No solution:", status())
