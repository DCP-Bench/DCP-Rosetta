# initials_queue: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/initials_queue.html
# Run it (after `pip install exact numpy`) with:
#   python initials_queue.py

from itertools import combinations

from exact import Exact


def create_model(instance):
    """Ten mathematicians stand in a queue. Each has two distinct initials from A to E in
    alphabetical order, nobody has the same initials as another, and nobody shares a
    letter with the person in front. BE is at the front, CD right behind, BD at the end."""
    n_people = 10  # people in the queue
    n_letters = 5  # the letters A to E, coded 0 to 4

    # The ten possible initials: two different letters in alphabetical order.
    pairs = list(combinations(range(n_letters), 2))
    # number[pair] is the position of that pair in pairs.
    number = {pair: idx for idx, pair in enumerate(pairs)}

    solver = Exact()

    # Exact identifies its variables by name.
    # has[i][p] is 1 when the person at place i, counting from the front, has the initials pairs[p].
    has = [[f"has_{i}_{p}" for p in range(len(pairs))] for i in range(n_people)]
    for i in range(n_people):
        for name in has[i]:
            solver.addVariable(name, 0, 1)
        # Each person has exactly one pair of initials.
        solver.addConstraint([(1, name) for name in has[i]], True, 1, True, 1)
    # Nobody has the same initials as anybody else.
    for p in range(len(pairs)):
        solver.addConstraint([(1, has[i][p]) for i in range(n_people)], False, 0, True, 1)

    # Nobody shares a letter with the person in front.
    for i in range(n_people - 1):
        for p, first in enumerate(pairs):
            for q, second in enumerate(pairs):
                if set(first) & set(second):
                    solver.addConstraint([(1, has[i][p]), (1, has[i + 1][q])], False, 0, True, 1)

    # The letters at the front: BE at place 0, CD at place 1 and BD at the last place, with B=1, C=2, D=3, E=4.
    fixed = {(0, 0): 1, (0, 1): 4, (1, 0): 2, (1, 1): 3, (n_people - 1, 0): 1, (n_people - 1, 1): 3}
    # queue[i][k] is the k-th initial of the person at place i, counting from the front, with A to E coded 0 to 4.
    queue = [[f"queue_{i}_{k}" for k in range(2)] for i in range(n_people)]
    for i in range(n_people):
        for k in range(2):
            if (i, k) in fixed:
                solver.addVariable(queue[i][k], fixed[(i, k)], fixed[(i, k)])
            else:
                solver.addVariable(queue[i][k], 0, n_letters - 1)
            # Each letter of the queue is the matching initial of the person there.
            terms = [(pair[k], has[i][p]) for p, pair in enumerate(pairs) if pair[k] != 0]
            solver.addConstraint(terms + [(-1, queue[i][k])], True, 0, True, 0)

    return solver, {"queue": queue}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
