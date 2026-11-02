# giant_cat_army: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/giant_cat_army.html
# Run it (after `pip install pulp numpy`) with:
#   python giant_cat_army.py

import math

import pulp


def create_model(instance):
    """Starting from the list [0], each step adds 5, adds 7 or takes the square root of
    the last number. Build a list of 24 distinct whole numbers, none above 60, that ends
    with 14 and contains 2 and 10 in that order, with other numbers allowed in between.
    The puzzle fixes all the data, so the instance is not used."""
    # The largest number allowed in the list.
    max_value = 60
    # The number of places in the list.
    n_places = 24
    values = range(max_value + 1)
    places = range(n_places)

    problem = pulp.LpProblem("giant_cat_army", pulp.LpMinimize)

    # holds[i][v] is 1 when the number at place i of the list is v, and 0 when not.
    # The first place holds 0 and the last holds 14.
    holds = []
    for i in places:
        row = []
        for v in values:
            if i == 0 or i == n_places - 1:
                lo = up = int(v == (0 if i == 0 else 14))
            else:
                lo, up = 0, 1
            row.append(pulp.LpVariable(f"holds_{i}_{v}", lowBound=lo, upBound=up, cat="Integer"))
        holds.append(row)

    # x[i] is the number at place i of the list.
    x = [pulp.lpSum(v * holds[i][v] for v in values) for i in places]

    # The numbers that may follow v in the list: v + 5, v + 7, and the square root of v
    # when that is a whole number.
    def successors(v):
        nxt = [w for w in (v + 5, v + 7) if w <= max_value]
        root = math.isqrt(v)
        if root * root == v:
            nxt.append(root)
        return nxt

    # Each place holds exactly one number.
    for i in places:
        problem += pulp.lpSum(holds[i]) == 1

    # All numbers in the list are distinct.
    for v in values:
        problem += pulp.lpSum(holds[i][v] for i in places) <= 1

    # The second number is 5 or 7.
    problem += holds[1][5] + holds[1][7] == 1

    # Each number is followed at the next place by one of its successors.
    for i in range(n_places - 1):
        for v in values:
            problem += holds[i][v] <= pulp.lpSum(holds[i + 1][w] for w in successors(v))

    # The numbers 2 and 10 each appear once, and 2 comes before 10.
    problem += pulp.lpSum(holds[i][2] for i in places) == 1
    problem += pulp.lpSum(holds[i][10] for i in places) == 1
    problem += (pulp.lpSum(i * holds[i][2] for i in places) + 1
                <= pulp.lpSum(i * holds[i][10] for i in places))

    return problem, {"x": x}


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
