# pythagorean_triplet: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/pythagorean_triplet.html
# Run it (after `pip install pulp numpy`) with:
#   python pythagorean_triplet.py

import pulp


def create_model(instance):
    """Pythagorean triplet (Project Euler 9): natural numbers a, b, c with a^2 + b^2 = c^2 and
    a + b + c = 1000."""
    total = 1000  # the sum a + b + c
    top = 500     # the largest value of each number: each is less than the sum of the other two, so less than half of 1000
    values = range(1, top + 1)

    # The puzzle asks for numbers that meet the conditions, so nothing is optimised.
    problem = pulp.LpProblem("pythagorean_triplet", pulp.LpMinimize)

    # a, b, c: the three numbers, each from 1 to top
    a = pulp.LpVariable("a", 1, top, cat="Integer")
    b = pulp.LpVariable("b", 1, top, cat="Integer")
    c = pulp.LpVariable("c", 1, top, cat="Integer")

    # The three numbers add up to 1000.
    problem += a + b + c == total

    # is_a[v] is 1 when a equals v. Exactly one value is chosen, and a is that value.
    is_a = {v: pulp.LpVariable(f"a_is_{v}", cat="Binary") for v in values}
    problem += pulp.lpSum(is_a.values()) == 1
    problem += a == pulp.lpSum(v * var for v, var in is_a.items())

    # Substituting c = 1000 - a - b into a^2 + b^2 = c^2 gives a * b = 1000 * (a + b) - 500000,
    # which has one product in place of three squares. share[v] is b when a equals v, and 0
    # otherwise. Then a * b is the sum of v * share[v].
    share = {v: pulp.LpVariable(f"share_{v}", 0, top) for v in values}
    for v, var in is_a.items():
        problem += share[v] <= top * var
        problem += share[v] <= b
        problem += share[v] >= b - top * (1 - var)
    problem += (pulp.lpSum(v * share[v] for v in values)
                == total * (a + b) - (total * total) // 2)

    return problem, {"a": a, "b": b, "c": c}


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
