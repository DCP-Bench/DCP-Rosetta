# csplib_006_golomb_rulers: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_006_golomb_rulers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_006_golomb_rulers.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_006_golomb_rulers.py csplib_006_golomb_rulers.json

from exact import Exact


def create_model(instance):
    """Place size marks on a ruler, the first at position 0, so that the differences between
    every pair of marks are all different. Find the shortest such ruler."""
    size = instance["size"]  # the number of marks

    solver = Exact()

    def triangular(k):
        """1 + 2 + ... + k, the smallest sum of k different positive whole numbers."""
        return k * (k + 1) // 2

    # the largest position a mark may take
    longest = size * size

    # low[i] and high[i] bound the position of mark i. The i gaps before mark i are different
    # positive whole numbers, so the mark is at least triangular(i). The size - 1 - i gaps after
    # it also fit on the ruler, so it is at most longest - triangular(size - 1 - i).
    low = [triangular(i) for i in range(size)]
    high = [longest - triangular(size - 1 - i) for i in range(size)]

    # Exact identifies its variables by name.
    # marks[i] is the position of mark i
    marks = [f"marks_{i}" for i in range(size)]
    for i in range(size):
        solver.addVariable(marks[i], low[i], high[i])

    # The first mark is at 0.
    solver.addConstraint([(1, marks[0])], True, 0, True, 0)

    # n_differences is the number of pairs of marks. Their differences are different positive whole
    # numbers, so the largest one, which is the length of the ruler, is at least that many.
    n_differences = size * (size - 1) // 2
    # length is the length of the ruler, the position of its last mark
    solver.addVariable("length", n_differences, longest)
    solver.addConstraint([(1, "length"), (-1, marks[size - 1])], True, 0, True, 0)

    # The marks are in strictly increasing order of position.
    for i in range(size - 1):
        solver.addConstraint([(1, marks[i + 1]), (-1, marks[i])], True, 1)

    # The ruler from mark i to mark j has j - i gaps, which are different positive whole numbers, so it is
    # at least triangular(j - i) long. The rest of the ruler, before mark i and after mark j, holds the i
    # gaps before mark i and the size - 1 - j gaps after mark j. The first to last mark has no rest.
    for i in range(size - 1):
        for j in range(i + 1, size):
            solver.addConstraint([(1, marks[j]), (-1, marks[i])], True, triangular(j - i))
            if (i, j) != (0, size - 1):
                solver.addConstraint([(1, "length"), (-1, marks[j]), (1, marks[i])],
                                     True, triangular(i) + triangular(size - 1 - j))

    # For each g, the pairs of marks at most g places apart number n_near_pairs. Their differences are
    # different positive whole numbers, so their sum is at least triangular(n_near_pairs). Summed over
    # the marks, each mark counts +1 for every such pair that it ends and -1 for every such pair that it starts.
    for g in range(1, size):
        n_near_pairs = sum(size - s for s in range(1, g + 1))
        weights = [(min(g, k) - min(g, size - 1 - k), marks[k]) for k in range(size)]
        solver.addConstraint([(w, name) for w, name in weights if w], True, triangular(n_near_pairs))

    # at_position[i][p] is 1 when mark i sits at position p
    at_position = [{p: f"mark_{i}_at_{p}" for p in range(low[i], high[i] + 1)} for i in range(size)]
    # has_mark[p] is 1 when some mark sits at position p
    has_mark = [f"has_mark_at_{p}" for p in range(longest + 1)]
    for p in range(longest + 1):
        solver.addVariable(has_mark[p], 0, 1)
    for i in range(size):
        for name in at_position[i].values():
            solver.addVariable(name, 0, 1)
        # mark i sits at exactly one position
        solver.addConstraint([(1, name) for name in at_position[i].values()], True, 1, True, 1)
        # the position of mark i is the one it sits at
        solver.addConstraint([(p, name) for p, name in at_position[i].items() if p] + [(-1, marks[i])],
                             True, 0, True, 0)
    # A position holds at most one mark, and holds one exactly when a mark sits there.
    for p in range(longest + 1):
        holders = [at_position[i][p] for i in range(size) if p in at_position[i]]
        solver.addConstraint([(1, name) for name in holders] + [(-1, has_mark[p])], True, 0, True, 0)

    # Each distance d occurs between at most one pair of marked positions. marks_at_p_and_pd is forced to
    # 1 when both positions p and p + d hold a mark.
    for d in range(1, longest + 1):
        at_distance = []
        for p in range(longest - d + 1):
            name = f"marks_at_{p}_and_{p + d}"
            solver.addVariable(name, 0, 1)
            solver.addConstraint([(1, name), (-1, has_mark[p]), (-1, has_mark[p + d])], True, -1)
            at_distance.append((1, name))
        solver.addConstraint(at_distance, False, 0, True, 1)

    # The objective is the length of the ruler: the shortest ruler is the best.
    solver.setObjective([(1, "length")], minimize=True)

    return solver, {"marks": marks, "length": "length"}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
