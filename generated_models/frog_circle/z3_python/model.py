# frog_circle: a Z3 (Python) model from DCP Rosetta.
# Download the `frog_circle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/frog_circle.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python frog_circle.py frog_circle.json

import z3


def create_model(instance):
    """Cards numbered 1 to n are arranged in a circle. A frog starts on card 1 and, from card k,
    jumps k places clockwise. Find an arrangement of the cards that lets the frog land on every
    card."""
    n = instance["n"]  # the number of cards, numbered 1 to n, and of places on the circle

    # x[p] is the number of the card at place p of the circle
    x = [z3.Int(f"x_{p}") for p in range(n)]
    # next_place[p] is the place the frog reaches from place p: x[p] places clockwise,
    # wrapping around the circle
    next_place = [z3.Int(f"next_place_{p}") for p in range(n)]
    # on[i][p] is true when the frog stands on place p after i jumps
    on = [[z3.Bool(f"on_{i}_{p}") for p in range(n)] for i in range(n)]

    solver = z3.Solver()

    # The cards are numbered 1 to n, each used once.
    solver.add([z3.And(1 <= xp, xp <= n) for xp in x])
    solver.add(z3.Distinct(x))

    # The frog starts on card 1, which sits at place 0.
    solver.add(x[0] == 1)
    solver.add([on[0][p] == (p == 0) for p in range(n)])

    # Each jump goes from the place the frog stands on to the place its card points to.
    solver.add([
        next_place[p] == z3.If(p + x[p] >= n, p + x[p] - n, p + x[p]) for p in range(n)
    ])

    # After each jump, the frog stands on the place reached from where it stood before.
    solver.add([
        on[i][q] == z3.Or([z3.And(on[i - 1][p], next_place[p] == q) for p in range(n)])
        for i in range(1, n) for q in range(n)
    ])

    # The frog stands on exactly one place at every step.
    solver.add([z3.PbEq([(on[i][p], 1) for p in range(n)], 1) for i in range(n)])

    # The frog stands on each place exactly once in its first n positions, so it lands on every card.
    solver.add([z3.PbEq([(on[i][p], 1) for i in range(n)], 1) for p in range(n)])

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
