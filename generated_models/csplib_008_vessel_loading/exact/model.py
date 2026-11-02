# csplib_008_vessel_loading: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_008_vessel_loading.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_008_vessel_loading.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_008_vessel_loading.py csplib_008_vessel_loading.json

from exact import Exact


def create_model(instance):
    """Decide whether a given set of containers can be laid out on a rectangular deck, in a single
    layer and parallel to the sides of the deck, without overlapping and with the minimum
    separation between the classes that require one. Each container may be turned a quarter turn."""
    deck_width = instance["deck_width"]    # the width of the deck, across it
    deck_length = instance["deck_length"]  # the length of the deck, along it
    n = instance["n_containers"]           # the number of containers
    width = instance["width"]              # width[i]: the width of container i, as listed
    length = instance["length"]            # length[i]: the length of container i, as listed
    classes = instance["classes"]          # classes[i]: the class of container i, 1-based
    separation = instance["separation"]    # separation[a][b]: the minimum distance between classes a + 1 and b + 1

    solver = Exact()

    # Exact identifies its variables by name.
    # left[i] and right[i] are the two sides of container i across the deck, and bottom[i] and top[i] are
    # its two sides along the deck. All four lie on the deck.
    left = [f"left_{i}" for i in range(n)]
    right = [f"right_{i}" for i in range(n)]
    top = [f"top_{i}" for i in range(n)]
    bottom = [f"bottom_{i}" for i in range(n)]
    for i in range(n):
        solver.addVariable(left[i], 0, deck_width)
        solver.addVariable(right[i], 0, deck_width)
        solver.addVariable(top[i], 0, deck_length)
        solver.addVariable(bottom[i], 0, deck_length)

    # turned[i] is 1 when container i is turned a quarter turn, so that it is length wide and width long.
    # Otherwise it is width wide and length long.
    for i in range(n):
        turned = f"turned_{i}"
        solver.addVariable(turned, 0, 1)
        # the container's extent across the deck is width[i], or length[i] when turned
        turn_effect = [(-(length[i] - width[i]), turned)] if length[i] != width[i] else []
        solver.addConstraint([(1, right[i]), (-1, left[i])] + turn_effect, True, width[i], True, width[i])
        # the container's extent along the deck is length[i], or width[i] when turned
        turn_effect = [(-(width[i] - length[i]), turned)] if length[i] != width[i] else []
        solver.addConstraint([(1, top[i]), (-1, bottom[i])] + turn_effect, True, length[i], True, length[i])

    # No two containers overlap, and containers of classes with a separation keep that distance apart.
    # For each pair, one of four cases holds: one container lies at least sep beyond the other, to the
    # left, to the right, below or above it. Each case gets a 0/1 variable that is 1 when the case holds.
    for x in range(n):
        for y in range(x + 1, n):
            sep = separation[classes[x] - 1][classes[y] - 1]
            cases = []
            for label, terms in (
                ("left_of", [(1, left[y]), (-1, right[x])]),   # x lies left of y
                ("right_of", [(1, left[x]), (-1, right[y])]),  # x lies right of y
                ("under", [(1, bottom[y]), (-1, top[x])]),     # x lies below y
                ("above", [(1, bottom[x]), (-1, top[y])]),     # x lies above y
            ):
                case = f"container_{x}_{label}_{y}"
                solver.addVariable(case, 0, 1)
                solver.addReification(case, True, terms, sep)
                cases.append((1, case))
            solver.addConstraint(cases, True, 1)

    return solver, {"left": left, "right": right, "top": top, "bottom": bottom}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
