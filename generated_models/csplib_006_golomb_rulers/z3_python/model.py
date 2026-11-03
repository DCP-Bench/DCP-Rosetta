# csplib_006_golomb_rulers: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_006_golomb_rulers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_006_golomb_rulers.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_006_golomb_rulers.py csplib_006_golomb_rulers.json

import z3


def create_model(instance):
    """Place size marks on a ruler, the first at position 0, so that the differences between
    all pairs of marks are distinct. Find the shortest such Golomb ruler."""
    size = instance["size"]  # the number of marks on the ruler

    # least[k] is a lower bound on the length of a ruler with k marks. Its k(k-1)/2 differences
    # are distinct positive numbers. Dropping its last mark leaves a ruler with k - 1 marks.
    # Cutting it at any mark gives two rulers whose lengths add up to its length.
    least = [0] * (size + 1)
    for k in range(2, size + 1):
        least[k] = max([k * (k - 1) // 2, least[k - 1] + 1]
                       + [least[a] + least[k + 1 - a] for a in range(2, k)])

    # No mark lies beyond position last_position = size * size.
    last_position = size * size

    # ge[i][p] is true when mark i lies at position p or beyond, for positions 1 to last_position.
    # Mark 0 is at position 0, so it has no row.
    ge = [None] + [[None] + [z3.Bool(f"ge_{i}_{p}") for p in range(1, last_position + 1)]
                   for i in range(1, size)]

    def at_least(i, p):
        """True when mark i lies at position p or beyond."""
        if p <= 0:
            return z3.BoolVal(True)
        if p > last_position or i == 0:
            return z3.BoolVal(False)
        return ge[i][p]

    solver = z3.Optimize()

    # A mark at position p + 1 or beyond is also at position p or beyond.
    for i in range(1, size):
        for p in range(1, last_position):
            solver.add(z3.Implies(ge[i][p + 1], ge[i][p]))

    # The marks are in increasing order. Marks i to j form a ruler with j - i + 1 marks, so they
    # span at least least[j - i + 1]: mark j lies that far beyond mark i.
    for i in range(size):
        for j in range(i + 1, size):
            gap = least[j - i + 1]
            for p in range(0, last_position + 1):
                solver.add(z3.Implies(at_least(i, p), at_least(j, p + gap)))

    # on[p] is true when a mark lies at position p. Mark i is at position p when it is at p or
    # beyond and not at p + 1 or beyond.
    on = [z3.Bool(f"on_{p}") for p in range(last_position + 1)]
    for i in range(size):
        for p in range(last_position + 1):
            solver.add(z3.Implies(z3.And(at_least(i, p), z3.Not(at_least(i, p + 1))), on[p]))

    # The ruler has exactly size marks.
    solver.add(z3.PbEq([(b, 1) for b in on], size))

    # The distances between pairs of marks are all different: no two pairs of marked positions
    # lie the same distance d apart.
    for d in range(1, last_position + 1):
        for p in range(last_position + 1 - d):
            for q in range(p + 1, last_position + 1 - d):
                solver.add(z3.Or(z3.Not(on[p]), z3.Not(on[p + d]),
                                 z3.Not(on[q]), z3.Not(on[q + d])))

    # k marks span at least least[k], so a stretch of least[k] consecutive positions holds at
    # most k - 1 marks.
    for k in range(3, size + 1):
        width = least[k]
        for p in range(last_position + 2 - width):
            solver.add(z3.AtMost(*on[p:p + width], k - 1))

    # marks[i] is the position of mark i.
    marks = []
    for i in range(size):
        position = z3.IntVal(last_position)
        for p in range(last_position, 0, -1):
            position = z3.If(z3.Not(at_least(i, p)), p - 1, position)
        marks.append(position)

    # The length of the ruler is the position of its last mark.
    length = marks[size - 1]

    # Minimise the length, counted as the positions from 1 upward at or beyond which the last mark lies.
    objective = z3.Sum([z3.If(at_least(size - 1, p), 1, 0) for p in range(1, last_position + 1)])
    solver.minimize(objective)

    return solver, {"marks": marks, "length": length}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
