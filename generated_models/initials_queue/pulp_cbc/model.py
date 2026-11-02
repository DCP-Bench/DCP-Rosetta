# initials_queue: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/initials_queue.html
# Run it (after `pip install pulp numpy`) with:
#   python initials_queue.py

from itertools import combinations

import pulp


def create_model(instance):
    """Ten people stand in a queue for a lecture. Each has initials that are an
    alphabetically ordered pair of distinct letters from A to E, no two people share
    their initials, and no one shares a letter with the person in front. BE is at the
    front, CD right behind and BD at the end. What are the initials of the queue?"""
    n_people = 10  # the people in the queue, counting from the front
    A, B, C, D, E = range(5)  # the letters A to E, as the numbers 0 to 4

    # The possible initials: alphabetically ordered pairs of distinct letters.
    pairs = list(combinations(range(5), 2))

    # A satisfaction problem: the clues alone fix the queue.
    problem = pulp.LpProblem("initials_queue", pulp.LpMinimize)

    # has[i][p] is 1 when the person at place i has the initials pairs[p], and 0 when not.
    has = [[pulp.LpVariable(f"has_{i}_{p[0]}{p[1]}", cat="Binary") for p in pairs]
           for i in range(n_people)]

    # Each person has exactly one pair of initials.
    for i in range(n_people):
        problem += pulp.lpSum(has[i]) == 1

    # No two people have the same initials.
    for k in range(len(pairs)):
        problem += pulp.lpSum(has[i][k] for i in range(n_people)) <= 1

    # No one shares a letter with the person in front of them.
    for i in range(n_people - 1):
        for k, p in enumerate(pairs):
            for q_index, q in enumerate(pairs):
                if set(p) & set(q):
                    problem += has[i][k] + has[i + 1][q_index] <= 1

    # BE is at the front, CD right behind and BD at the end.
    problem += has[0][pairs.index((B, E))] == 1
    problem += has[1][pairs.index((C, D))] == 1
    problem += has[n_people - 1][pairs.index((B, D))] == 1

    # queue[i] holds the two letters of the initials of the person at place i.
    queue = [[pulp.lpSum(p[side] * has[i][k] for k, p in enumerate(pairs)) for side in (0, 1)]
             for i in range(n_people)]

    return problem, {"queue": queue}


if __name__ == "__main__":
    import numpy as np

    problem, outputs = create_model({})
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
