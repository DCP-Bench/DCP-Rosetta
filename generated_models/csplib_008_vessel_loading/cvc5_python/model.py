# csplib_008_vessel_loading: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_008_vessel_loading.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_008_vessel_loading.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_008_vessel_loading.py csplib_008_vessel_loading.json

import cvc5.pythonic as c5


def create_model(instance):
    """Decide whether the containers can be laid out on the rectangular deck, each one
    parallel to the sides of the deck, without overlapping and with the required distance
    between containers of the classes that need one."""
    deck_width = instance["deck_width"]  # the width of the deck
    deck_length = instance["deck_length"]  # the length of the deck
    n = instance["n_containers"]  # the number of containers
    width = instance["width"]  # width[i]: the width of container i
    length = instance["length"]  # length[i]: the length of container i
    classes = instance["classes"]  # classes[i]: the class of container i
    separation = instance["separation"]  # separation[a][b]: the minimum distance between a container of class a + 1 and one of class b + 1

    # left[i] and right[i] are the sides of container i across the deck, bottom[i] and top[i]
    # are its sides along the deck
    left = [c5.Int(f"left_{i}") for i in range(n)]
    right = [c5.Int(f"right_{i}") for i in range(n)]
    bottom = [c5.Int(f"bottom_{i}") for i in range(n)]
    top = [c5.Int(f"top_{i}") for i in range(n)]

    # Linear integer logic: cvc5 solves this model much faster than with the default Solver().
    solver = c5.SolverFor("QF_LIA")

    # Each container lies on the deck.
    for i in range(n):
        solver.add(left[i] >= 0, bottom[i] >= 0, right[i] <= deck_width, top[i] <= deck_length)

    # Each container is turned either way: its width runs across the deck, or its length does.
    for i in range(n):
        solver.add(c5.Or(
            c5.And(right[i] - left[i] == width[i], top[i] - bottom[i] == length[i]),
            c5.And(right[i] - left[i] == length[i], top[i] - bottom[i] == width[i]),
        ))

    # Two containers do not overlap: one lies to one side of the other, with at least the
    # separation for their classes between them.
    for i in range(n):
        for j in range(i + 1, n):
            gap = separation[classes[i] - 1][classes[j] - 1]
            solver.add(c5.Or(
                right[i] + gap <= left[j],
                right[j] + gap <= left[i],
                top[i] + gap <= bottom[j],
                top[j] + gap <= bottom[i],
            ))

    return solver, {"left": left, "right": right, "top": top, "bottom": bottom}


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
