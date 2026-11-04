# csplib_006_golomb_rulers: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_006_golomb_rulers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_006_golomb_rulers.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_006_golomb_rulers.py csplib_006_golomb_rulers.json

import mip


def create_model(instance):
    """Golomb ruler: place `size` marks at integer positions 0 = a_1 < a_2 < ... < a_m so
    that the m(m-1)/2 differences a_j - a_i (i < j) are all distinct, and the length
    a_m of the ruler is as small as possible.

    The model reports the positions of the marks and the length of the ruler."""
    size = instance["size"]  # number of marks
    # The reference lets every mark lie between 0 and size * size; the model keeps
    # that range, so no mark lies beyond `horizon`.
    horizon = size * size

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Mark k (k = 0..size-1) is preceded by k marks and followed by size-1-k, all at
    # distinct positions, so it lies between k and horizon - (size - 1 - k). The
    # first mark is at 0.
    first = list(range(size))
    last = [0 if k == 0 else horizon - (size - 1 - k) for k in range(size)]

    # marks[k] = position of mark k (declared output); length = position of the
    # last mark (declared output)
    marks = [model.add_var(f"marks_{k}", lb=first[k], ub=last[k], var_type=mip.INTEGER)
             for k in range(size)]
    length = marks[size - 1]

    # objective: minimise the length of the ruler
    model.objective = length

    # the first mark is at 0, and the marks are increasing along the ruler
    model += marks[0] == 0
    for k in range(size - 1):
        model += marks[k] + 1 <= marks[k + 1]

    # Every pair of marks (i, j), i < j, has a difference a_j - a_i, and the
    # differences are all distinct. gives[(i, j)][d] = 1 if the difference of that
    # pair is d. The difference of marks i and j is the sum of the j - i gaps between
    # them; each gap is itself a difference, so the gaps are distinct positive
    # integers and any j - i of them add up to at least (j-i)(j-i+1)/2. The largest
    # difference is bounded by the room left on the ruler outside the pair.
    gives = {}
    for i in range(size):
        for j in range(i + 1, size):
            low = (j - i) * (j - i + 1) // 2
            high = last[j] - first[i]
            gives[(i, j)] = {d: model.add_var(f"gives_{i}_{j}_{d}", var_type=mip.BINARY)
                             for d in range(low, high + 1)}
            # the pair has exactly one difference, and it is a_j - a_i
            model += mip.xsum(gives[(i, j)].values()) == 1
            model += marks[j] - marks[i] == mip.xsum(
                d * var for d, var in gives[(i, j)].items())

    # all differences are distinct: each value d is the difference of at most one pair
    for d in range(1, horizon + 1):
        users = [pair[d] for pair in gives.values() if d in pair]
        if len(users) > 1:
            model += mip.xsum(users) <= 1

    # Implied bound that tightens the relaxation: the size*(size-1)/2 differences are
    # distinct positive integers no larger than the length, so the length is at
    # least size*(size-1)/2.
    model += length >= size * (size - 1) // 2

    return model, {"marks": marks, "length": length}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
