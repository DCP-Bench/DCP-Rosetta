# csplib_008_vessel_loading: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_008_vessel_loading.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_008_vessel_loading.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_008_vessel_loading.py csplib_008_vessel_loading.json

import z3


def create_model(instance):
    """Decide whether the containers can be laid out on a rectangular deck, parallel to its
    sides, without overlapping and with the minimum separation between their classes."""
    deck_width = instance["deck_width"]    # the width of the deck, across it
    deck_length = instance["deck_length"]  # the length of the deck, along it
    n_containers = instance["n_containers"]  # the number of containers
    width = instance["width"]              # width[i]: the width of container i
    length = instance["length"]            # length[i]: the length of container i
    classes = instance["classes"]          # classes[i]: the class of container i
    separation = instance["separation"]    # separation[a][b]: the minimum gap between a container of class a + 1 and one of class b + 1

    # left[i] and right[i] are the sides of container i across the deck. bottom[i] and top[i] are
    # its sides along the deck.
    left = [z3.Int(f"left_{i}") for i in range(n_containers)]
    right = [z3.Int(f"right_{i}") for i in range(n_containers)]
    top = [z3.Int(f"top_{i}") for i in range(n_containers)]
    bottom = [z3.Int(f"bottom_{i}") for i in range(n_containers)]

    solver = z3.Solver()

    # Every container lies on the deck.
    for i in range(n_containers):
        solver.add(z3.And(left[i] >= 0, left[i] <= deck_width))
        solver.add(z3.And(right[i] >= 0, right[i] <= deck_width))
        solver.add(z3.And(top[i] >= 0, top[i] <= deck_length))
        solver.add(z3.And(bottom[i] >= 0, bottom[i] <= deck_length))

    # Each container shows either its width or its length across the deck.
    for i in range(n_containers):
        solver.add(z3.Or(
            z3.And(right[i] - left[i] == width[i], top[i] - bottom[i] == length[i]),
            z3.And(right[i] - left[i] == length[i], top[i] - bottom[i] == width[i])))

    # Two containers do not overlap: one lies left of, right of, above or below the other, with
    # at least the separation between their classes in between.
    for x in range(n_containers):
        for y in range(x + 1, n_containers):
            gap = separation[classes[x] - 1][classes[y] - 1]
            solver.add(z3.Or(right[x] + gap <= left[y],
                             left[x] >= right[y] + gap,
                             top[x] + gap <= bottom[y],
                             bottom[x] >= top[y] + gap))

    return solver, {"left": left, "right": right, "top": top, "bottom": bottom}


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
