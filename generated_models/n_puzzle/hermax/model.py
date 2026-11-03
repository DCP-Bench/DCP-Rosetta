# n_puzzle: a hermax (Python) model from DCP Rosetta.
# Download the `n_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/n_puzzle.html
# Then run it on the first instance (after `pip install hermax`):
#   python n_puzzle.py n_puzzle.json

from hermax.model import Model


def create_model(instance):
    """The N-puzzle: a square board of numbered tiles with one empty cell (value 0).
    Starting from the start board, slide a tile into the empty cell one move per step,
    every step changing the board, so that after N_STEPS - 1 moves the board is the end
    board. The answer is the board at every step, start and end included."""
    start = instance["puzzle_start"]  # start[i][j]: the value in row i, column j of the first board, 0 = empty
    end = instance["puzzle_end"]      # end[i][j]: the value in row i, column j of the last board, 0 = empty
    n_steps = instance["N_STEPS"]     # number of boards to print, start and end included
    dim = len(start)                  # the board is dim by dim
    n_cells = dim * dim               # cells are numbered row by row, 0 .. n_cells - 1
    n_tiles = n_cells - 1             # tiles are numbered 1 .. n_tiles; 0 is the empty cell

    m = Model()

    # board[t][c] is the value in cell c at step t (0 = the empty cell)
    board = [[m.int(f"board_{t}_{c}", 0, n_tiles) for c in range(n_cells)]
             for t in range(n_steps)]

    # Every board is a full arrangement: each tile and the empty cell appears exactly once.
    for t in range(n_steps):
        m &= m.vector(board[t]).all_different()

    # The first board is the start board and the last board is the end board.
    for c in range(n_cells):
        i, j = divmod(c, dim)
        m &= (board[0][c] == start[i][j])
        m &= (board[n_steps - 1][c] == end[i][j])

    def neighbours(c):
        """The cells sharing a side with cell c."""
        i, j = divmod(c, dim)
        return [(i + di) * dim + (j + dj) for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1))
                if 0 <= i + di < dim and 0 <= j + dj < dim]

    for t in range(n_steps - 1):
        # Exactly one move per step: the empty cell slides from cell c to a neighbouring cell d.
        moves = [(c, d) for c in range(n_cells) for d in neighbours(c)]
        # move[k] is true when the step is moves[k]
        move = m.bool_vector(f"move_{t}", len(moves))
        m &= move.exactly_one()
        for k, (c, d) in enumerate(moves):
            # the empty cell is in c before the move and in d after it
            m &= (~move[k] | (board[t][c] == 0))
            m &= (~move[k] | (board[t + 1][d] == 0))
            # the tile that was in d slides into c
            m &= (board[t + 1][c] == board[t][d]).only_if(move[k])

        # Every other cell keeps its tile: it is unchanged, or it is one of the two cells of the move.
        for c in range(n_cells):
            same = m.bool()
            m &= (board[t + 1][c] == board[t][c]).iff(same)
            m &= (same | (board[t][c] == 0) | (board[t + 1][c] == 0))

    # steps[t][i][j]: the value in row i, column j of the board at step t (the declared output)
    steps = [[[board[t][i * dim + j] for j in range(dim)] for i in range(dim)]
             for t in range(n_steps)]

    return m, {"steps": steps}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
