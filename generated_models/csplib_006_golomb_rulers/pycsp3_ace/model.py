# csplib_006_golomb_rulers: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_006_golomb_rulers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_006_golomb_rulers.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_006_golomb_rulers.py csplib_006_golomb_rulers.json

from pycsp3 import *


def create_model(instance):
    """A Golomb ruler is a set of m integers 0 = a_1 < a_2 < ... < a_m such that the
    m(m-1)/2 differences a_j - a_i (1 <= i < j <= m) are all distinct. The ruler has m
    marks and length a_m. Find a ruler of minimum length."""
    n_marks = instance["size"]  # m, the number of marks on the ruler

    # Upper bound on the length, assumed and not proven: a ruler with n_marks marks is taken to be
    # no longer than n_marks * n_marks, far above the known optimal lengths of the instances.
    max_length = n_marks * n_marks

    # marks[i] is the position of mark i + 1 on the ruler, the first mark at 0
    marks = VarArray(size=n_marks, dom=range(max_length + 1))
    # length is the position of the last mark, the length of the ruler
    length = Var(dom=range(max_length + 1))

    satisfy(
        # the first mark is at 0
        marks[0] == 0,
        # the marks are in strictly increasing order
        Increasing(marks, strict=True),
        # the length of the ruler is the position of its last mark a_m
        length == marks[-1],
        # all differences between pairs of marks are distinct
        AllDifferent(marks[j] - marks[i] for i in range(n_marks) for j in range(i + 1, n_marks)),
    )

    # The objective: the length of the ruler is minimised.
    minimize(length)

    return {"marks": marks, "length": length}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        print("marks", "=", values(outputs["marks"]))
        print("length", "=", value(outputs["length"]))
    else:
        print("No solution:", status())
