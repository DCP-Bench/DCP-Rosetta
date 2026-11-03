# n_puzzle: a Choco-solver (Python) model from DCP Rosetta.
# Download the `n_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/n_puzzle.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python n_puzzle.py n_puzzle.json

from pychoco.model import Model


def create_model(instance):
    """N-puzzle: on a square board with tiles 1 to n_tiles and one empty square (0),
    find the boards at each of N_STEPS steps, from the start board to the end board.
    Every step slides one tile into the empty square, and the board changes at every
    step."""
    n_steps = instance["N_STEPS"]            # the number of boards, including the start and end boards
    puzzle_start = instance["puzzle_start"]  # the start board
    puzzle_end = instance["puzzle_end"]      # the end board
    dim = len(puzzle_start)                  # the board is dim x dim squares
    n_tiles = dim * dim - 1                  # the number of numbered tiles
    n_cells = dim * dim                      # the number of squares

    model = Model()

    # steps[t][i][j]: the tile in row i, column j at step t (0 is the empty square)
    steps = [[[model.intvar(0, n_tiles, name=f"steps_{t}_{i}_{j}") for j in range(dim)]
              for i in range(dim)] for t in range(n_steps)]
    # flat[t]: all the squares of the board at step t, in one list
    flat = [[steps[t][i][j] for i in range(dim) for j in range(dim)] for t in range(n_steps)]
    # empty[t][i][j] is true when the empty square is at row i, column j at step t
    empty = [[[model.arithm(steps[t][i][j], "=", 0).reify() for j in range(dim)]
              for i in range(dim)] for t in range(n_steps)]

    # The first board is the start board and the last board is the end board.
    for i in range(dim):
        for j in range(dim):
            model.arithm(steps[0][i][j], "=", puzzle_start[i][j]).post()
            model.arithm(steps[-1][i][j], "=", puzzle_end[i][j]).post()

    # The square at row i, column j and the squares next to it, above, below, left and right.
    def neighbours(i, j):
        for di, dj in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]:
            if 0 <= i + di < dim and 0 <= j + dj < dim:
                yield i + di, j + dj

    for t in range(1, n_steps):
        before, after = steps[t - 1], steps[t]

        # The empty square moves to a neighbouring square or stays where it is: a square
        # that is empty after the step was empty before it, or next to it.
        for i in range(dim):
            for j in range(dim):
                # came_from: the squares the empty square could have come from
                came_from = [empty[t - 1][r][c] for r, c in neighbours(i, j)]
                model.sum(came_from, ">=", empty[t][i][j]).post()

        # Each tile is on exactly one square of the board.
        model.all_different(flat[t]).post()

        # Only the empty square moves: a square keeps its tile unless the empty square
        # is on it before or after the step.
        # unchanged: the squares whose tile is the same before and after the step
        unchanged = []
        for i in range(dim):
            for j in range(dim):
                # same is true when the square keeps its tile
                same = model.arithm(before[i][j], "=", after[i][j]).reify()
                unchanged.append(same)
                model.sum([empty[t - 1][i][j], empty[t][i][j], same], ">=", 1).post()

        # The board changes at every step: not every square keeps its tile.
        model.sum(unchanged, "<", n_cells).post()

    # Implied constraints. They follow from the rules above and only rule out dead ends
    # sooner, which matters for puzzles with a long solution.

    # position[t][k]: the square that holds tile k at step t (k = 0 is the empty square)
    position = [[model.intvar(0, n_cells - 1, name=f"position_{t}_{k}") for k in range(n_cells)]
                for t in range(n_steps)]
    # Each position matches its board: tile k sits on the square position[t][k].
    for t in range(n_steps):
        model.inverse_channeling(flat[t], position[t]).post()

    # adjacent_cells: the pairs of squares that share an edge
    adjacent_cells = [[a, b] for a in range(n_cells) for b in range(n_cells)
                      if abs(a // dim - b // dim) + abs(a % dim - b % dim) == 1]
    # The empty square moves to a square next to its old one at every step.
    for t in range(1, n_steps):
        model.table([position[t - 1][0], position[t][0]], adjacent_cells).post()

    # The tile on the square the empty square moves to slides into the square it leaves.
    for t in range(1, n_steps):
        # moved: the tile that slides at step t
        moved = model.intvar(1, n_tiles, name=f"moved_{t}")
        model.element(moved, flat[t - 1], position[t][0]).post()
        model.element(moved, flat[t], position[t - 1][0]).post()

    # goal_cell[k]: the square that tile k must reach on the end board
    goal_cell = {puzzle_end[i][j]: i * dim + j for i in range(dim) for j in range(dim)}
    # Each step moves one tile by one square, so the total distance of the tiles from
    # their goal squares falls by at most 1 per step. At step t that total cannot be
    # more than the number of steps still to come.
    for t in range(n_steps):
        # distances: the distance of each tile from its goal square
        distances = []
        for k in range(1, n_cells):
            gr, gc = divmod(goal_cell[k], dim)
            # distance_to_goal[c]: the distance from square c to the goal square of tile k
            distance_to_goal = [abs(c // dim - gr) + abs(c % dim - gc) for c in range(n_cells)]
            # distance: the distance of tile k from its goal square, at most the longest distance on the board
            distance = model.intvar(0, 2 * (dim - 1), name=f"distance_{t}_{k}")
            model.element(distance, distance_to_goal, position[t][k]).post()
            distances.append(distance)
        model.sum(distances, "<=", n_steps - 1 - t).post()

    return model, {"steps": steps}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
