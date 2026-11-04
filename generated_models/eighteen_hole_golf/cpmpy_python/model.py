# eighteen_hole_golf: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/eighteen_hole_golf.html
# Run it (after `pip install cpmpy`) with:
#   python eighteen_hole_golf.py

import cpmpy as cp


def create_model(instance):
    """A golf course has 18 holes, each of length 3, 4 or 5,
    and the total length of the course is 72."""
    num_holes = 18      # the course has 18 holes
    total_length = 72   # the lengths of all holes add up to 72

    # holes[i] is the length of hole i
    holes = cp.intvar(3, 5, shape=num_holes, name="holes")

    model = cp.Model()
    # The hole lengths add up to the length of the course.
    model.add(cp.sum(holes) == total_length)

    return model, {"holes": holes}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
