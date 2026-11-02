# initials_queue: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/initials_queue.html
# Run it (after `pip install cvc5 numpy`) with:
#   python initials_queue.py

import cvc5.pythonic as c5


def create_model(instance):
    """Ten people stand in a queue, each with two different letters from A to E in alphabetical order. No two people have the same initials, and nobody shares a letter with the person in front. BE is at the front, CD right behind, and BD at the end."""
    n = 10  # people in the queue

    # The five letters A to E, as the integers 0 to 4.
    A, B, C, D, E = range(5)

    # a[i] and b[i] are the first and second initial of the person at place i in the queue.
    a = [c5.Int(f"a_{i}") for i in range(n)]
    b = [c5.Int(f"b_{i}") for i in range(n)]

    # All constraints on the queue.
    solver = c5.Solver()

    # Every initial is one of the letters A to E.
    for i in range(n):
        solver.add(a[i] >= A, a[i] <= E, b[i] >= A, b[i] <= E)

    # The two initials of each person are different letters, in alphabetical order.
    solver.add([a[i] < b[i] for i in range(n)])

    # No two people have the same initials.
    solver.add([c5.Or(a[i] != a[j], b[i] != b[j]) for i in range(n) for j in range(i + 1, n)])

    # Nobody shares a letter with the person in front of them.
    for i in range(n - 1):
        solver.add([x != y for x in (a[i], b[i]) for y in (a[i + 1], b[i + 1])])

    # BE is at the front of the queue, CD right behind, and BD at the end.
    solver.add(a[0] == B, b[0] == E, a[1] == C, b[1] == D, a[n - 1] == B, b[n - 1] == D)

    # The initials of the person at each place in the queue.
    queue = [[a[i], b[i]] for i in range(n)]
    return solver, {"queue": queue}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
