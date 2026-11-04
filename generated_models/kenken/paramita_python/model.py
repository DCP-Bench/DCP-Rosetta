# kenken: a Paramita (Python) model from DCP Rosetta.
# Download the `kenken.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kenken.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python kenken.py kenken.json

from itertools import product as cartesian
from math import prod

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, Or, add_to_container, to_cnf


def _table(name, cells, holds, allowed):
    """Return a flag and the constraints under which the flag being true means the cells
    hold one of the allowed tuples of digits."""
    flag = Bool(name)
    if not allowed:
        return flag, [~flag]
    constraints = []
    picks = []  # picks[i] stands for the i-th allowed tuple
    for i, tup in enumerate(allowed):
        pick = Bool(f"{name}_{i}")
        for cell, v in zip(cells, tup):
            constraints.append(If(pick, holds[cell][v]))
        picks.append(pick)
    constraints.append(If(flag, Or(picks)))
    return flag, constraints


def create_model(instance):
    """Fill an n by n grid with the digits 1 to n so that every row and every column holds
    each digit once. Each cage has a target that its digits reach under one of the four
    arithmetic operations. The operation of each cage is not given."""
    n = instance["n"]              # the grid is n by n
    digits = range(1, n + 1)       # the digits 1 to n
    cells_all = [(r, c) for r in range(1, n + 1) for c in range(1, n + 1)]  # every cell of the grid
    cages = instance["problem"]    # each cage: its target, then the cells it covers, as [row, col] (1-based)

    # holds[(r, c)][v] is true when the cell in row r, column c holds digit v
    holds = {cell: {v: Bool(f"x_{cell[0]}_{cell[1]}_{v}") for v in digits} for cell in cells_all}

    cons = []  # the rules of the puzzle

    # Each cell holds exactly one digit.
    for cell in cells_all:
        cons.append(sum(holds[cell].values()) == 1)

    # Each row holds each digit exactly once.
    for r in range(1, n + 1):
        for v in digits:
            cons.append(sum(holds[(r, c)][v] for c in range(1, n + 1)) == 1)

    # Each column holds each digit exactly once.
    for c in range(1, n + 1):
        for v in digits:
            cons.append(sum(holds[(r, c)][v] for r in range(1, n + 1)) == 1)

    # Each cage reaches its target under one of its operations.
    for ci, (target, cage_cells) in enumerate(cages):
        cells = [tuple(cell) for cell in cage_cells]
        tag = f"cage_{ci}"

        # A single-cell cage holds its target.
        if len(cells) == 1:
            cons.append(holds[cells[0]][target])
            continue

        flags = []  # the operations this cage can use

        # Sum: the digits of the cage add up to the target.
        sum_flag = Bool(f"{tag}_sum")
        flags.append(sum_flag)
        cons.append(If(
            sum_flag,
            sum(v * holds[cell][v] for cell in cells for v in digits) == target,
        ))

        # Product: the digits of the cage multiply to the target.
        product_tuples = [t for t in cartesian(digits, repeat=len(cells)) if prod(t) == target]
        flag, table = _table(f"{tag}_product", cells, holds, product_tuples)
        flags.append(flag)
        cons.extend(table)

        # A two-cell cage may also use difference or exact quotient.
        if len(cells) == 2:
            # Difference: the larger digit minus the smaller is the target.
            diff_tuples = [t for t in cartesian(digits, repeat=2) if abs(t[0] - t[1]) == target]
            flag, table = _table(f"{tag}_difference", cells, holds, diff_tuples)
            flags.append(flag)
            cons.extend(table)

            # Quotient: the larger digit divided by the smaller is the target.
            quot_tuples = [t for t in cartesian(digits, repeat=2) if max(t) == target * min(t)]
            flag, table = _table(f"{tag}_quotient", cells, holds, quot_tuples)
            flags.append(flag)
            cons.extend(table)

        # One of the operations must hold.
        cons.append(Or(flags))

    # x[r][c] is the digit in the cell at row r, column c.
    x = []
    for r in range(1, n + 1):
        x.append([sum(v * holds[(r, c)][v] for v in digits) for c in range(1, n + 1)])

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in cons:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"x": x}


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
