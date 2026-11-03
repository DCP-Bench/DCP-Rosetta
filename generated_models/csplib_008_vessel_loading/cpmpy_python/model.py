# csplib_008_vessel_loading: a CPMpy model from DCP Rosetta.
# Download the `csplib_008_vessel_loading.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_008_vessel_loading.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_008_vessel_loading.py csplib_008_vessel_loading.json

import itertools

import cpmpy as cp


def create_model(instance):
    """Decide whether containers can be laid out on a rectangular deck without overlapping
    and without violating the minimum separation distances between classes of containers."""
    deck_width = instance["deck_width"]   # the width of the deck
    deck_length = instance["deck_length"] # the length of the deck
    n = instance["n_containers"]          # the number of containers
    width = instance["width"]             # width[i]: the width of container i
    length = instance["length"]           # length[i]: the length of container i
    classes = instance["classes"]         # classes[i]: the class (1-based) of container i
    separation = instance["separation"]   # separation[a][b]: minimum distance between classes a+1 and b+1

    # left[i] and right[i] are the sides of container i across the deck;
    # bottom[i] and top[i] are its sides along the deck
    left = cp.intvar(0, deck_width, shape=n, name="left")
    right = cp.intvar(0, deck_width, shape=n, name="right")
    top = cp.intvar(0, deck_length, shape=n, name="top")
    bottom = cp.intvar(0, deck_length, shape=n, name="bottom")

    model = cp.Model()

    # Each container has its own size, in either orientation.
    for i in range(n):
        model.add(((right[i] - left[i] == width[i]) & (top[i] - bottom[i] == length[i]))
                  | ((right[i] - left[i] == length[i]) & (top[i] - bottom[i] == width[i])))

    # Two containers do not overlap: one lies left of, right of, above or below the other,
    # with at least the separation distance between their classes in between.
    for a, b in itertools.combinations(range(n), 2):
        sep = separation[classes[a] - 1][classes[b] - 1]
        model.add((right[a] + sep <= left[b])
                  | (left[a] >= right[b] + sep)
                  | (top[a] + sep <= bottom[b])
                  | (bottom[a] >= top[b] + sep))

    return model, {"left": left, "right": right, "top": top, "bottom": bottom}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
