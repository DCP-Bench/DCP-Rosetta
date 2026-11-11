# flow_free_game: a CPLEX (Python) model from DCP Rosetta.
# Download the `flow_free_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flow_free_game.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python flow_free_game.py flow_free_game.json

from docplex.mp.model import Model


def create_model(instance):
    """Flow Free: colour every cell of the board so that each pair of equally coloured end points
    is joined by a pipe; an end point has exactly one neighbour of its colour and every other
    cell exactly two."""
    board = instance["board"]  # board[i][j] is the colour of an end point, or 0 if empty
    M = len(board)     # number of rows
    N = len(board[0])  # number of columns
    # The colours are the numbers on the board, 1 up to the largest of them.
    max_colour = max(max(row) for row in board)

    model = Model("flow_free_game")

    # B[i][j] is the colour of cell (i, j); an end point keeps its given colour.
    B = [[model.integer_var(board[i][j] if board[i][j] else 1,
                            board[i][j] if board[i][j] else max_colour, name=f"B_{i}_{j}")
          for j in range(N)] for i in range(M)]

    # same[edge] is 1 exactly when two orthogonally adjacent cells have the same colour.
    # Each such equivalence costs one binary and one constraint, which is smaller than
    # comparing one-hot colour vectors.
    same = {}
    for i in range(M):
        for j in range(N):
            for k, l in ((i + 1, j), (i, j + 1)):
                if k < M and l < N:
                    e = model.binary_var(name=f"same_{i}_{j}_{k}_{l}")
                    model.add_equivalence(e, B[i][j] == B[k][l])
                    same[(i, j), (k, l)] = e
                    same[(k, l), (i, j)] = e

    def neighbours(i, j):
        return [(k, l) for k, l in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1))
                if 0 <= k < M and 0 <= l < N]

    for i in range(M):
        for j in range(N):
            same_neighs = model.sum(same[(i, j), c] for c in neighbours(i, j))
            if board[i][j] != 0:
                # An end point continues its pipe into exactly one neighbour.
                model.add_constraint(same_neighs == 1)
            else:
                # Any other cell lies inside a pipe: exactly two neighbours share its colour.
                model.add_constraint(same_neighs == 2)

    return model, {"B": B}


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
