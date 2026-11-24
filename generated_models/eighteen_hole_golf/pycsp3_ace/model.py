# eighteen_hole_golf: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/eighteen_hole_golf.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python eighteen_hole_golf.py

from pycsp3 import *


def create_model(instance):
    """Generate an 18-hole golf course where each hole has a length of 3, 4, or 5,
    and the total length of the course is 72."""
    n_holes = 18  # the number of holes on the course
    min_length = 3  # the shortest allowed hole length
    max_length = 5  # the longest allowed hole length
    total_length = 72  # the required total length of the course

    # holes[i] is the length of hole i, one of min_length to max_length
    holes = VarArray(size=n_holes, dom=range(min_length, max_length + 1))

    satisfy(
        # The lengths of the holes add up to the total length of the course.
        Sum(holes) == total_length,
    )

    return {"holes": holes}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
