# csplib_012_nonogram: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_012_nonogram.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_012_nonogram.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_012_nonogram.py csplib_012_nonogram.json

from functools import reduce

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, Iff, add_to_container, to_cnf


# True when at least one of the expressions in xs is true.
def any_of(xs):
    return reduce(lambda a, b: a | b, xs)


def line_constraints(tag, cells, blocks):
    """Constraints that make the shaded squares of one row or column show the given blocks,
    in order, with at least one unshaded square between two blocks.

    cells: the shaded flags of the line, in order. blocks: the block lengths, zeros removed.
    """
    width = len(cells)
    constraints = []
    if not blocks:
        # An empty line: no square is shaded.
        constraints += [~cells[c] for c in range(width)]
        return constraints

    n_blocks = len(blocks)
    # starts[k][t] is true when block k begins at square t. Only the squares where the whole
    # block fits are listed.
    starts = []
    for k, length in enumerate(blocks):
        starts.append({t: Bool(f"{tag}_start_{k}_{t}") for t in range(width - length + 1)})

    # begun[k][t] is true when block k begins at square t or earlier.
    begun = []
    for k in range(n_blocks):
        flags = [Bool(f"{tag}_begun_{k}_{t}") for t in range(width)]
        begun.append(flags)
        for t in range(width):
            options = []
            if t > 0:
                options.append(flags[t - 1])
            if t in starts[k]:
                options.append(starts[k][t])
            # Block k has begun by square t when it had begun by the square before, or begins
            # at square t. With no such option, it has not begun by square t.
            if options:
                constraints.append(Iff(flags[t], any_of(options)))
            else:
                constraints.append(~flags[t])

    # Each block begins at exactly one square.
    for k in range(n_blocks):
        constraints.append(sum(starts[k].values()) == 1)

    # Blocks keep their order: block k begins at square t only if block k - 1 begins by square
    # t - length(k - 1) - 1, which leaves one unshaded square between the two blocks.
    for k in range(1, n_blocks):
        prev_length = blocks[k - 1]
        for t, s in starts[k].items():
            u = t - prev_length - 1
            if u >= 0:
                constraints.append(If(s, begun[k - 1][u]))
            else:
                constraints.append(~s)

    # A square is shaded exactly when some block covers it. Block k covers square c when it
    # begins in the length(k) squares that end at c.
    for c in range(width):
        covers = []
        for k, length in enumerate(blocks):
            if c - length >= 0:
                covers.append(begun[k][c] & ~begun[k][c - length])
            else:
                covers.append(begun[k][c])
        constraints.append(Iff(cells[c], any_of(covers)))
    return constraints


def create_model(instance):
    """Shade squares of a grid so that the shaded squares of every row and column form the
    blocks given by its rule, in order."""
    n_rows = instance["rows"]  # the number of rows
    n_cols = instance["cols"]  # the number of columns
    # row_rules[r]: the block lengths of row r, in order, with zeros up to row_rule_len.
    row_rules = instance["row_rules"]
    # col_rules[c]: the block lengths of column c, in order, with zeros up to col_rule_len.
    col_rules = instance["col_rules"]

    # shade[r][c] is true when the square in row r and column c is shaded.
    shade = [[Bool(f"shade_{r}_{c}") for c in range(n_cols)] for r in range(n_rows)]

    constraints = []
    # Each row shows its blocks.
    for r in range(n_rows):
        blocks = [v for v in row_rules[r] if v > 0]
        constraints += line_constraints(f"row{r}", shade[r], blocks)
    # Each column shows its blocks.
    for c in range(n_cols):
        blocks = [v for v in col_rules[c] if v > 0]
        constraints += line_constraints(f"col{c}", [shade[r][c] for r in range(n_rows)], blocks)

    # The board: 1 for a shaded square, 0 for an unshaded one.
    board = [[1 * shade[r][c] for c in range(n_cols)] for r in range(n_rows)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"board": board}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

    solver = SatSolver.from_name("Cadical300")
    # copy the formula into the solver
    solver.add_clauses(formula.clauses())

    if solver.solve():
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
