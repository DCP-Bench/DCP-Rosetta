# frog_circle: a cvc5 (Python) model from DCP Rosetta.
# Download the `frog_circle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/frog_circle.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python frog_circle.py frog_circle.json

import cvc5.pythonic as c5


def create_model(instance):
    """Cards numbered 1 to n are arranged in a circle. A frog starts on card 1 and, from card k,
    jumps k places clockwise. Find an arrangement of the cards that lets the frog land on every
    card. Print the arrangement (x)."""
    n = instance["n"]  # the number of cards

    # x[p] is the card at place p around the circle, counting clockwise from place 0.
    x = c5.Ints([f"x{p}" for p in range(n)])
    # step[p] is the step at which the frog lands on place p. The frog starts on place 0 at step 0.
    step = c5.Ints([f"step{p}" for p in range(n)])
    # landing[p] is the place the frog jumps to from place p, counting around the circle.
    landing = [c5.If(p + x[p] >= n, p + x[p] - n, p + x[p]) for p in range(n)]

    # Each card number is from 1 to n, and each landing step is from 0 to n-1.
    bounds = ([v >= 1 for v in x] + [v <= n for v in x]
              + [s >= 0 for s in step] + [s <= n - 1 for s in step])

    # From place p the frog jumps to landing[p]. Until its last step, the place it lands on is
    # the one it visits at the next step.
    jumps = [c5.Implies(c5.And(step[p] < n - 1, landing[p] == q), step[q] == step[p] + 1)
             for p in range(n) for q in range(n)]

    solver = c5.Solver()

    solver.add(bounds + [
        # The cards are all different, and so are the steps.
        c5.Distinct(x),
        c5.Distinct(step),
        # The frog starts on card 1, at place 0, at step 0.
        x[0] == 1,
        step[0] == 0,
    ] + jumps)

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
