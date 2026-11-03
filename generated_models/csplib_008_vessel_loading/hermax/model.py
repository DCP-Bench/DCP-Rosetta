# csplib_008_vessel_loading: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_008_vessel_loading.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_008_vessel_loading.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_008_vessel_loading.py csplib_008_vessel_loading.json

from hermax.model import Model


def create_model(instance):
    """Vessel loading (CSPLib prob008): place rectangular containers on a rectangular deck,
    lying flat and parallel to the deck sides (each may be turned by 90 degrees), without
    overlapping, and with containers of classes that must be kept apart separated by at least
    the required distance along or across the deck. A satisfaction problem: find any placement."""
    deck_width = instance["deck_width"]    # the deck's extent from left to right
    deck_length = instance["deck_length"]  # the deck's extent from bottom to top
    width = instance["width"]              # width[i]: left-to-right size of container i when not turned
    length = instance["length"]            # length[i]: bottom-to-top size of container i when not turned
    classes = instance["classes"]          # classes[i]: the class of container i, numbered from 1
    separation = instance["separation"]    # separation[a][b]: the gap needed between classes a+1 and b+1
    n = len(width)                         # the number of containers

    m = Model()

    # left[i] and right[i] bound container i from left to right, right being just past its last column
    left = m.int_vector("left", n, 0, deck_width)
    right = m.int_vector("right", n, 0, deck_width)
    # bottom[i] and top[i] bound container i from bottom to top, top being just past its last row
    bottom = m.int_vector("bottom", n, 0, deck_length)
    top = m.int_vector("top", n, 0, deck_length)
    # turned[i] is true when container i is turned by 90 degrees, swapping its two sizes
    turned = m.bool_vector("turned", n)

    # Each container spans its width and length on the deck, swapped when it is turned.
    for i in range(n):
        m &= (right[i] - left[i] == width[i]).only_if(~turned[i])
        m &= (top[i] - bottom[i] == length[i]).only_if(~turned[i])
        m &= (right[i] - left[i] == length[i]).only_if(turned[i])
        m &= (top[i] - bottom[i] == width[i]).only_if(turned[i])

    # Containers must not overlap, and must be kept apart by the separation between their classes.
    # For each pair, one of the four sides must separate them by the required distance
    # (0 when their classes have no requirement between them).
    for i in range(n):
        for j in range(i + 1, n):
            gap = separation[classes[i] - 1][classes[j] - 1]
            # Each side is a choice: one Boolean per side says that it is the one used.
            j_right_of_i = m.bool()   # j lies to the right of i, at least gap columns away
            i_right_of_j = m.bool()   # i lies to the right of j, at least gap columns away
            j_above_i = m.bool()      # j lies above i, at least gap rows away
            i_above_j = m.bool()      # i lies above j, at least gap rows away
            m &= (left[j] - right[i] >= gap).iff(j_right_of_i)
            m &= (left[i] - right[j] >= gap).iff(i_right_of_j)
            m &= (bottom[j] - top[i] >= gap).iff(j_above_i)
            m &= (bottom[i] - top[j] >= gap).iff(i_above_j)
            # At least one side must hold.
            m &= (j_right_of_i | i_right_of_j | j_above_i | i_above_j)

    # Satisfaction problem: no objective.
    outputs = {"left": left, "right": right, "top": top, "bottom": bottom}
    return m, outputs


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
