# csplib_008_vessel_loading: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_008_vessel_loading.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_008_vessel_loading.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_008_vessel_loading.py csplib_008_vessel_loading.json

import itertools

from ortools.sat.python import cp_model


def create_model(instance):
    """Decide whether a given set of containers can be laid out on a rectangular deck,
    in a single layer and parallel to the sides of the deck, without overlapping and
    without breaking the minimum separation between the classes of containers."""
    deck_width = instance["deck_width"]        # the width of the deck
    deck_length = instance["deck_length"]      # the length of the deck
    n_containers = instance["n_containers"]    # the number of containers
    width = instance["width"]                  # width[i]: the width of container i
    length = instance["length"]                # length[i]: the length of container i
    classes = instance["classes"]              # classes[i]: the class of container i
    separation = instance["separation"]        # separation[a][b]: the minimum gap between containers of classes a + 1 and b + 1

    model = cp_model.CpModel()

    # left[i] and right[i] are the sides of container i across the deck,
    # bottom[i] and top[i] are its sides along the deck
    left = [model.new_int_var(0, deck_width, f"left_{i}") for i in range(n_containers)]
    right = [model.new_int_var(0, deck_width, f"right_{i}") for i in range(n_containers)]
    top = [model.new_int_var(0, deck_length, f"top_{i}") for i in range(n_containers)]
    bottom = [model.new_int_var(0, deck_length, f"bottom_{i}") for i in range(n_containers)]

    # Each container lies upright, with its width across the deck, or turned, with its length across it.
    # upright[i] is true when container i is upright.
    for i in range(n_containers):
        upright = model.new_bool_var(f"upright_{i}")
        model.add(right[i] - left[i] == width[i]).only_enforce_if(upright)
        model.add(top[i] - bottom[i] == length[i]).only_enforce_if(upright)
        model.add(right[i] - left[i] == length[i]).only_enforce_if(~upright)
        model.add(top[i] - bottom[i] == width[i]).only_enforce_if(~upright)

    # Two containers do not overlap: one lies left of, right of, below or above the other,
    # with at least the separation distance between their classes in between.
    for x, y in itertools.combinations(range(n_containers), 2):
        sep = separation[classes[x] - 1][classes[y] - 1]
        # placements[k] is one of the four ways x and y can lie apart: x left of y, y left of x,
        # x below y or y below x
        placements = [(right[x] + sep, left[y]), (right[y] + sep, left[x]),
                      (top[x] + sep, bottom[y]), (top[y] + sep, bottom[x])]
        # ways[k] is true when placement k holds
        ways = []
        for k, (lower, upper) in enumerate(placements):
            way = model.new_bool_var(f"apart_{x}_{y}_{k}")
            model.add(lower <= upper).only_enforce_if(way)
            ways.append(way)
        model.add_bool_or(ways)

    return model, {"left": left, "right": right, "top": top, "bottom": bottom}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
