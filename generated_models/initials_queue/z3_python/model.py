# initials_queue: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/initials_queue.html
# Run it (after `pip install z3-solver numpy`) with:
#   python initials_queue.py

import z3


def create_model(instance):
    """Ten people stand in a queue, each with two distinct initials from A to E in alphabetical
    order. No two people have the same initials, and nobody shares a letter with the person in
    front of them. BE is at the front, CD right behind, and BD at the end. What are the initials
    of the ten people, from the front?"""
    n = 10  # people in the queue

    # the letters A to E
    A, B, C, D, E = range(5)

    # queue[i] holds the two initials of the person at place i in the queue
    queue = [[z3.Int(f"queue_{i}_{k}") for k in range(2)] for i in range(n)]

    solver = z3.Solver()

    # Every initial is one of the letters A to E.
    solver.add([z3.And(A <= letter, letter <= E) for pair in queue for letter in pair])

    # The two initials of each person are distinct and in alphabetical order.
    solver.add([first < second for first, second in queue])

    # No two people have the same initials.
    for i in range(n):
        for j in range(i + 1, n):
            solver.add(z3.Or(queue[i][0] != queue[j][0], queue[i][1] != queue[j][1]))

    # Nobody shares a letter with the person in front of them.
    for i in range(n - 1):
        for front in queue[i]:
            for behind in queue[i + 1]:
                solver.add(front != behind)

    # BE is at the front, CD right behind, and BD at the very end.
    solver.add(
        queue[0][0] == B, queue[0][1] == E,
        queue[1][0] == C, queue[1][1] == D,
        queue[n - 1][0] == B, queue[n - 1][1] == D,
    )

    return solver, {"queue": queue}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
