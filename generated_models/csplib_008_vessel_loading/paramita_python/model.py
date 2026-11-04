# csplib_008_vessel_loading: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_008_vessel_loading.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_008_vessel_loading.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_008_vessel_loading.py csplib_008_vessel_loading.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, Or, add_to_container, to_cnf


def create_model(instance):
    """Load rectangular containers in one layer on a rectangular deck, without overlap
    and with the required gap between containers of separated classes. A container may
    be turned by 90 degrees."""
    deck_width = instance["deck_width"]          # the width of the deck, along x
    deck_length = instance["deck_length"]        # the length of the deck, along y
    n_containers = instance["n_containers"]      # the number of containers
    width = instance["width"]                    # width[c]: the width of container c
    length = instance["length"]                  # length[c]: the length of container c
    classes = instance["classes"]                # classes[c]: the class of container c
    separation = instance["separation"]          # separation[a][b]: the least gap between containers of classes a and b

    # rot[c] is true when container c is turned, so its width runs along the deck length.
    # A square container looks the same turned, so it gets the constant 0 instead.
    rot = [Bool(f"rotated_{c}") if width[c] != length[c] else 0 for c in range(n_containers)]

    # at_left[c][x] is true when the left edge of container c is at x
    at_left = [
        {x: Bool(f"left_{c}_{x}") for x in range(deck_width - min(width[c], length[c]) + 1)}
        for c in range(n_containers)
    ]
    # at_bottom[c][y] is true when the bottom edge of container c is at y
    at_bottom = [
        {y: Bool(f"bottom_{c}_{y}") for y in range(deck_length - min(width[c], length[c]) + 1)}
        for c in range(n_containers)
    ]

    constraints = []

    # Each container has exactly one left edge position and one bottom edge position.
    constraints += [sum(at_left[c].values()) == 1 for c in range(n_containers)]
    constraints += [sum(at_bottom[c].values()) == 1 for c in range(n_containers)]

    # The left and bottom edges of each container.
    left = [sum(x * b for x, b in at_left[c].items()) for c in range(n_containers)]
    bottom = [sum(y * b for y, b in at_bottom[c].items()) for c in range(n_containers)]
    # The right and top edges, from the width and length as the container is turned.
    right = [left[c] + width[c] + (length[c] - width[c]) * rot[c] for c in range(n_containers)]
    top = [bottom[c] + length[c] + (width[c] - length[c]) * rot[c] for c in range(n_containers)]

    # Every container lies within the deck.
    constraints += [right[c] <= deck_width for c in range(n_containers)]
    constraints += [top[c] <= deck_length for c in range(n_containers)]

    # Two containers do not overlap, and containers of classes with a required gap keep
    # it. One of four ways holds for each pair: one container is to the left of the
    # other, or below it, with the gap between them.
    for i in range(n_containers):
        for j in range(i + 1, n_containers):
            gap = separation[classes[i] - 1][classes[j] - 1]
            ways = [
                right[i] + gap <= left[j],
                right[j] + gap <= left[i],
                top[i] + gap <= bottom[j],
                top[j] + gap <= bottom[i],
            ]
            # apart[k] is true when way k is the one that holds for containers i and j
            apart = [Bool(f"apart_{i}_{j}_{k}") for k in range(4)]
            constraints.append(Or(apart))
            constraints += [If(apart[k], ways[k]) for k in range(4)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"left": left, "right": right, "top": top, "bottom": bottom}


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
