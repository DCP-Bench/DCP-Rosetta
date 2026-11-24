# csplib_008_vessel_loading: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_008_vessel_loading.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_008_vessel_loading.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_008_vessel_loading.py csplib_008_vessel_loading.json

from pycsp3 import *


def create_model(instance):
    """Containers are cuboids laid out in a single layer on a rectangular deck, all parallel to
    the sides of the deck, and they must not overlap. Containers of some classes must be kept
    a minimum distance apart, along the deck or across it. Decide whether all containers can be
    positioned on the deck. Each container may be rotated by 90 degrees."""
    deck_width = instance["deck_width"]  # the size of the deck across its width
    deck_length = instance["deck_length"]  # the size of the deck along its length
    n_containers = instance["n_containers"]  # the number of containers to place
    container_class = instance["classes"]  # container_class[i] is the class of container i, numbered from 1
    container_width = instance["width"]  # container_width[i] is the width of container i across the deck
    container_length = instance["length"]  # container_length[i] is the length of container i along the deck
    separation = instance["separation"]  # separation[a-1][b-1] is the distance classes a and b must keep in at least one direction

    # left[i] and right[i] are the edges of container i across the width of the deck, each between 0 and deck_width
    left = VarArray(size=n_containers, dom=range(deck_width + 1))
    right = VarArray(size=n_containers, dom=range(deck_width + 1))
    # bottom[i] and top[i] are the edges of container i along the length of the deck, each between 0 and deck_length
    bottom = VarArray(size=n_containers, dom=range(deck_length + 1))
    top = VarArray(size=n_containers, dom=range(deck_length + 1))

    # the distance that each pair of containers i < j must keep, from the separation of their classes
    pairs = [
        (i, j, separation[container_class[i] - 1][container_class[j] - 1])
        for i in range(n_containers)
        for j in range(i + 1, n_containers)
    ]

    satisfy(
        # each container has its width across the deck and its length along it, or both turned by 90 degrees
        [
            Or(
                And(right[i] - left[i] == container_width[i], top[i] - bottom[i] == container_length[i]),
                And(right[i] - left[i] == container_length[i], top[i] - bottom[i] == container_width[i]),
            )
            for i in range(n_containers)
        ],
        # containers of classes a and b are apart by separation[a-1][b-1] in at least one direction;
        # with a distance of 0 this is the no-overlap condition, and touching is allowed
        [
            Or(
                left[j] - right[i] >= gap,
                left[i] - right[j] >= gap,
                bottom[j] - top[i] >= gap,
                bottom[i] - top[j] >= gap,
            )
            for i, j, gap in pairs
        ],
    )

    return {"left": left, "right": right, "top": top, "bottom": bottom}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
