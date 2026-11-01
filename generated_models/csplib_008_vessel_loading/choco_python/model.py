# csplib_008_vessel_loading: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_008_vessel_loading.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_008_vessel_loading.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_008_vessel_loading.py csplib_008_vessel_loading.json

from pychoco.model import Model


def create_model(instance):
    """Vessel loading: decide whether a given set of containers can be laid out on a rectangular
    deck in a single layer, parallel to the sides of the deck, without overlapping and with the
    required minimum distance between containers of certain classes."""
    deck_width = instance["deck_width"]      # the width of the deck
    deck_length = instance["deck_length"]    # the length of the deck
    n_containers = instance["n_containers"]  # the number of containers
    width = instance["width"]                # width[i]: the width of container i
    length = instance["length"]              # length[i]: the length of container i
    classes = instance["classes"]            # classes[i]: the class of container i, counted from 1
    separation = instance["separation"]      # separation[a - 1][b - 1]: the minimum distance between containers of classes a and b

    model = Model()

    # left[i] and right[i] are the two sides of container i across the deck.
    left = [model.intvar(0, deck_width, name=f"left_{i}") for i in range(n_containers)]
    right = [model.intvar(0, deck_width, name=f"right_{i}") for i in range(n_containers)]

    # bottom[i] and top[i] are the two sides of container i along the deck.
    bottom = [model.intvar(0, deck_length, name=f"bottom_{i}") for i in range(n_containers)]
    top = [model.intvar(0, deck_length, name=f"top_{i}") for i in range(n_containers)]

    # Container i has its width across the deck and its length along it, or the other way round when turned.
    for i in range(n_containers):
        across = model.intvar(0, deck_width, name=f"across_{i}")
        along = model.intvar(0, deck_length, name=f"along_{i}")

        # orientations lists the allowed pairs (across, along); a square container has only one.
        orientations = [[width[i], length[i]]]
        if width[i] != length[i]:
            orientations.append([length[i], width[i]])
        model.table([across, along], orientations).post()

        model.arithm(left[i], "+", across, "=", right[i]).post()
        model.arithm(bottom[i], "+", along, "=", top[i]).post()

    # Two containers do not overlap: one lies left of, right of, below or above the other,
    # with the separation for their classes between them.
    for x in range(n_containers):
        for y in range(x + 1, n_containers):
            sep = separation[classes[x] - 1][classes[y] - 1]
            model.or_([
                model.arithm(right[x], "+", sep, "<=", left[y]),
                model.arithm(right[y], "+", sep, "<=", left[x]),
                model.arithm(top[x], "+", sep, "<=", bottom[y]),
                model.arithm(top[y], "+", sep, "<=", bottom[x]),
            ]).post()

    return model, {"left": left, "right": right, "top": top, "bottom": bottom}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
