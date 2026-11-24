# clock_triplets: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/clock_triplets.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python clock_triplets.py

from pycsp3 import *


def create_model(instance):
    """Rearrange the numbers on the face of a clock (1 to 12) so no triplet of adjacent
    numbers has a sum higher than 21. This is the smallest value that the highest sum of
    a triplet can have."""
    n_numbers = 12  # the numbers 1 to 12, one per position on the clock face
    max_triplet_sum = 21  # the largest sum allowed for a triplet of adjacent numbers, from the statement

    # x[p] is the number at clock position p (positions 0 to 11, going round the face)
    x = VarArray(size=n_numbers, dom=range(1, n_numbers + 1))

    satisfy(
        # Each of the numbers 1 to 12 appears once on the face.
        AllDifferent(x),
        # No triplet of adjacent positions sums to more than max_triplet_sum. The face is a
        # circle, so the triplets at the end wrap round to positions 0 and 1.
        [
            x[p] + x[(p + 1) % n_numbers] + x[(p + 2) % n_numbers] <= max_triplet_sum
            for p in range(n_numbers)
        ],
    )

    return {"x": x}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
