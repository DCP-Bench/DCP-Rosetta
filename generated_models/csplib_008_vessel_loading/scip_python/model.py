# csplib_008_vessel_loading: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_008_vessel_loading.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_008_vessel_loading.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_008_vessel_loading.py csplib_008_vessel_loading.json

from itertools import combinations

from pyscipopt import Model


def create_model(instance):
    """Vessel loading: rectangular containers must be placed on a rectangular deck,
    parallel to its sides, without overlapping. Containers of some classes must also
    keep a minimum distance from each other. Each container may be turned by 90 degrees.
    Returns the model and the position of every container on the deck."""
    deck_width = instance["deck_width"]    # the deck's extent along x, from its left edge to its right edge
    deck_length = instance["deck_length"]  # the deck's extent along y, from its bottom edge to its top edge
    n = instance["n_containers"]           # the number of containers
    width = instance["width"]              # width[i]: x extent of container i when not turned
    length = instance["length"]            # length[i]: y extent of container i when not turned
    classes = instance["classes"]          # classes[i]: class of container i; classes are numbered from 1
    # separation[a-1][b-1]: minimum distance between containers of classes a and b
    separation = instance["separation"]

    model = Model("csplib_008_vessel_loading")

    # Container i covers the x range [left[i], right[i]) and the y range [bottom[i], top[i]), where
    # the upper edges right[i] and top[i] are the first unit past the container. So right[i] - left[i]
    # is its x extent and top[i] - bottom[i] its y extent. The deck spans 0..deck_width in x and
    # 0..deck_length in y, which bounds every edge and keeps each container on the deck.
    left = [model.addVar(name=f"left_{i}", vtype="I", lb=0, ub=deck_width) for i in range(n)]
    right = [model.addVar(name=f"right_{i}", vtype="I", lb=0, ub=deck_width) for i in range(n)]
    bottom = [model.addVar(name=f"bottom_{i}", vtype="I", lb=0, ub=deck_length) for i in range(n)]
    top = [model.addVar(name=f"top_{i}", vtype="I", lb=0, ub=deck_length) for i in range(n)]
    # turned[i] is 1 when container i is turned by 90 degrees, so its length runs along x.
    # The description fixes only that containers are parallel to the deck's sides, not which
    # of the two sides is their x extent, so both orientations are allowed.
    turned = [model.addVar(name=f"turned_{i}", vtype="B") for i in range(n)]

    # Extents: turned[i] = 0 gives container i an x extent of width[i] and a y extent of length[i];
    # turned[i] = 1 swaps the two. width and length are data, so both extents are linear in turned[i].
    for i in range(n):
        model.addCons(right[i] - left[i] == width[i] + (length[i] - width[i]) * turned[i])
        model.addCons(top[i] - bottom[i] == length[i] + (width[i] - length[i]) * turned[i])

    # Separation: every pair of containers i < j must be apart on the deck, either along x or
    # along y, by at least the minimum distance for their classes. A distance of 0 is plain
    # non-overlap. Assumption: separation[a-1][b-1] == separation[b-1][a-1], so the distance for
    # the pair does not depend on which container comes first; the code reads the entry in index order.
    for i, j in combinations(range(n), 2):
        gap = separation[classes[i] - 1][classes[j] - 1]
        # One binary per way the pair can be apart: j is right of i, i is right of j,
        # j is above i, or i is above j.
        j_right_of_i = model.addVar(name=f"j_right_of_i_{i}_{j}", vtype="B")
        i_right_of_j = model.addVar(name=f"i_right_of_j_{i}_{j}", vtype="B")
        j_above_i = model.addVar(name=f"j_above_i_{i}_{j}", vtype="B")
        i_above_j = model.addVar(name=f"i_above_j_{i}_{j}", vtype="B")
        # When a binary is 1, its side holds: the later container starts at least gap past
        # the end of the earlier one.
        model.addConsIndicator(right[i] + gap <= left[j], binvar=j_right_of_i)
        model.addConsIndicator(right[j] + gap <= left[i], binvar=i_right_of_j)
        model.addConsIndicator(top[i] + gap <= bottom[j], binvar=j_above_i)
        model.addConsIndicator(top[j] + gap <= bottom[i], binvar=i_above_j)
        # At least one of the four sides holds for every pair of containers.
        model.addCons(j_right_of_i + i_right_of_j + j_above_i + i_above_j >= 1)

    # No objective: the question is whether the containers fit, so any placement that satisfies
    # every constraint is an answer.
    outputs = {"left": left, "right": right, "top": top, "bottom": bottom}
    return model, outputs


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
