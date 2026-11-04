# three_coins: a Paramita (Python) model from DCP Rosetta.
# Download the `three_coins.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_coins.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python three_coins.py three_coins.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, Iff, add_to_container, to_cnf


def create_model(instance):
    """Three coins lie on a table, in the order tails, heads, tails. In exactly the given
    number of moves, each move flipping one coin over, make them all face heads or all
    face tails."""
    init = instance["init"]        # init[i]: whether coin i starts tails up
    n_moves = instance["num_moves"]  # the number of moves
    n_coins = len(init)            # the number of coins

    # steps[k][i] is true when coin i faces tails after k moves; k = 0 is the start
    steps = [[Bool(f"s_{k}_{i}") for i in range(n_coins)] for k in range(n_moves + 1)]
    # flips[k][i] is true when move k flips coin i
    flips = [[Bool(f"m_{k}_{i}") for i in range(n_coins)] for k in range(n_moves)]

    constraints = []

    # The coins start in the order given.
    for i in range(n_coins):
        constraints.append(steps[0][i] if init[i] else ~steps[0][i])

    # Each move flips exactly one coin.
    for k in range(n_moves):
        constraints.append(sum(flips[k]) == 1)

    # A move flips the coin it picks and leaves the other coins as they are.
    for k in range(n_moves):
        for i in range(n_coins):
            constraints.append(If(flips[k][i], Iff(steps[k + 1][i], ~steps[k][i])))
            constraints.append(If(~flips[k][i], Iff(steps[k + 1][i], steps[k][i])))

    # After the last move all the coins face the same way.
    last = steps[n_moves]
    constraints += [Iff(last[i], last[i + 1]) for i in range(n_coins - 1)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"steps": steps}


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
