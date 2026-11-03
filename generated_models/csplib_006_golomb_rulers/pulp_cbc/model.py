# csplib_006_golomb_rulers: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_006_golomb_rulers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_006_golomb_rulers.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_006_golomb_rulers.py csplib_006_golomb_rulers.json

import pulp


def create_model(instance):
    """Place marks on a ruler, the first at position 0, so that the differences between
    all pairs of marks are distinct. Find the shortest such Golomb ruler."""
    size = instance["size"]  # the number of marks on the ruler

    # No mark is placed beyond this position. The shortest ruler is far shorter.
    horizon = size * size

    problem = pulp.LpProblem("golomb_ruler", pulp.LpMinimize)

    # Mark k has k marks before it and size - 1 - k marks after it, all at distinct
    # positions, so it lies between k and horizon - (size - 1 - k). The first mark is at 0.
    earliest = list(range(size))
    latest = [0 if k == 0 else horizon - (size - 1 - k) for k in range(size)]

    # marks[k] is the position of mark k on the ruler
    marks = [pulp.LpVariable(f"marks_{k}", earliest[k], latest[k], cat="Integer")
             for k in range(size)]
    # The length of the ruler is the position of its last mark.
    length = marks[size - 1]

    # The marks are placed in increasing order along the ruler.
    for k in range(size - 1):
        problem += marks[k] + 1 <= marks[k + 1]

    # The difference between two marks i < j is the sum of the j - i gaps between them.
    # Each gap is a distance between marks, so the gaps are distinct positive integers,
    # and any j - i of them add up to at least (j - i)(j - i + 1) / 2. The difference is
    # at most the room left on the ruler outside the pair.
    # differences[(i, j)][d] is 1 when the difference of marks i and j is d.
    differences = {}
    for i in range(size):
        for j in range(i + 1, size):
            low = (j - i) * (j - i + 1) // 2
            high = latest[j] - earliest[i]
            differences[(i, j)] = {d: pulp.LpVariable(f"difference_{i}_{j}_{d}", cat="Binary")
                                   for d in range(low, high + 1)}
            # Each pair has exactly one difference, and it equals the distance between the marks.
            problem += pulp.lpSum(differences[(i, j)].values()) == 1
            problem += marks[j] - marks[i] == pulp.lpSum(
                d * choice for d, choice in differences[(i, j)].items())

    # All differences are distinct: each distance is the difference of at most one pair.
    for d in range(1, horizon + 1):
        pairs_with_d = [pair[d] for pair in differences.values() if d in pair]
        if len(pairs_with_d) > 1:
            problem += pulp.lpSum(pairs_with_d) <= 1

    # The size * (size - 1) / 2 differences are distinct positive integers, none larger
    # than the length of the ruler. So the length is at least that many.
    problem += length >= size * (size - 1) // 2

    # The objective is to minimise the length of the ruler.
    problem += length

    return problem, {"marks": marks, "length": length}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
