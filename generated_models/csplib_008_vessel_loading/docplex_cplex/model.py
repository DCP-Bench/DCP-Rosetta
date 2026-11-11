# csplib_008_vessel_loading: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_008_vessel_loading.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_008_vessel_loading.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_008_vessel_loading.py csplib_008_vessel_loading.json

from docplex.mp.model import Model


def create_model(instance):
    """Vessel loading: can the given containers be positioned in a single layer on a rectangular
    deck, parallel to its sides (a container may be turned a quarter turn), without overlapping
    and without violating the minimum separations between certain classes of containers?"""
    deck_width = instance["deck_width"]    # the size of the deck across
    deck_length = instance["deck_length"]  # the size of the deck along
    n = instance["n_containers"]           # number of containers
    width = instance["width"]            # width of each container
    length = instance["length"]          # length of each container
    classes = instance["classes"]        # class of each container, counted from 1
    separation = instance["separation"]  # least distance between containers of two classes

    model = Model("vessel_loading")

    # turned[i] is 1 when container i is turned a quarter turn: its extent along the deck
    # then is its length instead of its width.
    turned = [model.binary_var(name=f"turned_{i}") for i in range(n)]

    # left[i] and bottom[i] are the lower-left corner of container i on the deck.
    left = [model.integer_var(0, deck_width, name=f"left_{i}") for i in range(n)]
    bottom = [model.integer_var(0, deck_length, name=f"bottom_{i}") for i in range(n)]

    # The shape of container i: right - left is its width and top - bottom its length, or the
    # other way round when it is turned.
    right = [left[i] + width[i] + (length[i] - width[i]) * turned[i] for i in range(n)]
    top = [bottom[i] + length[i] - (length[i] - width[i]) * turned[i] for i in range(n)]

    # Every container lies on the deck.
    model.add_constraints(right[i] <= deck_width for i in range(n))
    model.add_constraints(top[i] <= deck_length for i in range(n))

    # No two containers overlap, and they keep the separation of their classes: container x is
    # at least `sep` to the left of y, to the right of y, below y or above y. Two binaries p, q
    # choose which of these four holds, as in the table
    #     (p, q) = (0, 0): x left of y     (1, 0): y left of x
    #              (0, 1): x below y       (1, 1): y below x
    # Each row below is relaxed by a bound times a factor that is at least 1, except for its
    # own choice, where the factor is 0. The bound is the largest the left-hand side can be, so
    # a relaxed row never binds.
    for x in range(n):
        for y in range(x + 1, n):
            sep = separation[classes[x] - 1][classes[y] - 1]
            across = deck_width + sep    # largest value of a left-right gap term
            along = deck_length + sep    # largest value of a top-bottom gap term
            p = model.binary_var(name=f"p_{x}_{y}")
            q = model.binary_var(name=f"q_{x}_{y}")
            model.add_constraint(right[x] + sep - left[y] <= across * (p + q))
            model.add_constraint(right[y] + sep - left[x] <= across * (1 - p + q))
            model.add_constraint(top[x] + sep - bottom[y] <= along * (1 + p - q))
            model.add_constraint(top[y] + sep - bottom[x] <= along * (2 - p - q))

    return model, {"left": left, "right": right, "top": top, "bottom": bottom}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
