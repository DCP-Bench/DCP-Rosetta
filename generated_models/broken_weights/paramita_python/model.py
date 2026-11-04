# broken_weights: a Paramita (Python) model from DCP Rosetta.
# Download the `broken_weights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/broken_weights.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python broken_weights.py broken_weights.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, Or, add_to_container, to_cnf


def any_of(xs):
    return xs[0] if len(xs) == 1 else Or(xs)


def create_model(instance):
    """A measuring weight of m pounds broke into n_pieces pieces, each a whole number of
    pounds. The pieces must weigh every whole load from 1 to m on a balance scale, with a
    piece allowed on either pan."""
    m = instance["m"]          # the total weight of the measure, in pounds
    n_pieces = instance["n"]   # the number of pieces it broke into

    # x[i][v - 1] is true when piece i weighs v pounds
    x = [[Bool(f"x_{i}_{v}") for v in range(1, m + 1)] for i in range(n_pieces)]
    # w[i] is the weight of piece i, in pounds
    w = [sum(v * x[i][v - 1] for v in range(1, m + 1)) for i in range(n_pieces)]
    # all constraints of the model
    cons = []

    # Each piece weighs one whole number of pounds.
    cons += [sum(x[i]) == 1 for i in range(n_pieces)]

    # The pieces add up to the whole weight.
    cons.append(sum(w) == m)

    # The pieces are listed in increasing weight, so no two weigh the same.
    cons += [w[i] < w[i + 1] for i in range(n_pieces - 1)]

    # A placement puts each piece on the load's pan, on the other pan, or off the scale.
    # A piece on the other pan counts negative. reach[s] is true when the pieces placed so
    # far give a net weight of s pounds; prev is the layer for the pieces before piece i,
    # cur the layer after it.
    empty = Bool("reach_0_0")
    cons.append(empty)
    prev = {0: empty}
    for i in range(n_pieces):
        cur = {}
        for s in range(-m, m + 1):
            # ways for net weight s after piece i: piece i is off the scale, or it is added
            # to or taken from an earlier net weight
            options = []
            if s in prev:
                options.append(prev[s])
            for v in range(1, m + 1):
                srcs = [prev[t] for t in (s - v, s + v) if t in prev]
                if srcs:
                    options.append(x[i][v - 1] & any_of(srcs))
            if not options:
                continue
            r = Bool(f"reach_{i + 1}_{s + m}")
            cur[s] = r
            cons.append(If(r, any_of(options)))
        prev = cur

    # Every load from 1 to m is balanced by a placement of the pieces.
    for load in range(1, m + 1):
        if load not in prev:
            raise ValueError("no way to weigh %d" % load)
        cons.append(prev[load])

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in cons:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"weights": w}


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
