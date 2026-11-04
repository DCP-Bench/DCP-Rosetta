# age_changing: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/age_changing.html
# Run it (after `pip install pulp numpy`) with:
#   python age_changing.py

import pulp


def create_model(instance):
    """Start with my age and apply the four operations +2, /8, -3 and *7 in some
    order: the result is my husband's age. Starting with his age and applying the
    same four operations in a different order gives my age. What are our ages?"""
    # The ages are not given: we assume adult ages between 16 and 120.
    age_low, age_high = 16, 120
    # Every value along the way is a whole number from 1 to 1000; the puzzle does not bound it.
    value_low, value_high = 1, 1000

    # Each operation as a * new + b * old + c == 0, where new is the result and old the value before.
    # +2: new = old + 2; /8: 8 * new = old; -3: new = old - 3; *7: new = 7 * old.
    operations = [(1, -1, -2), (8, -1, 0), (1, -1, 3), (1, -7, 0)]
    n = len(operations)

    def span(a, b, c):
        # The smallest and largest values that a * new + b * old + c can take.
        ends = [a * new + b * old + c for new in (value_low, value_high)
                for old in (value_low, value_high)]
        return min(ends), max(ends)

    problem = pulp.LpProblem("age_changing", pulp.LpMinimize)

    # My age.
    m = pulp.LpVariable("m", age_low, age_high, cat="Integer")
    # My husband's age.
    h = pulp.LpVariable("h", age_low, age_high, cat="Integer")

    # from_mine[i] is the value after the first i operations, starting from my age.
    from_mine = [pulp.LpVariable(f"from_mine_{i}", value_low, value_high, cat="Integer")
                 for i in range(n + 1)]
    # from_his[i] is the value after the first i operations, starting from his age.
    from_his = [pulp.LpVariable(f"from_his_{i}", value_low, value_high, cat="Integer")
                for i in range(n + 1)]

    # mine_order[i][k] is 1 when operation k is the one applied at step i, starting from my age.
    mine_order = [[pulp.LpVariable(f"mine_order_{i}_{k}", cat="Binary") for k in range(n)]
                  for i in range(n)]
    # his_order[i][k] is 1 when operation k is the one applied at step i, starting from his age.
    his_order = [[pulp.LpVariable(f"his_order_{i}_{k}", cat="Binary") for k in range(n)]
                 for i in range(n)]

    # Each step applies one operation, and each operation is applied at one step.
    for order in (mine_order, his_order):
        for i in range(n):
            problem += pulp.lpSum(order[i]) == 1
        for k in range(n):
            problem += pulp.lpSum(order[i][k] for i in range(n)) == 1

    # agree[i][k] is 1 when both orders apply operation k at step i.
    agree = [[pulp.LpVariable(f"agree_{i}_{k}", cat="Binary") for k in range(n)]
             for i in range(n)]
    # The two orders differ: they do not agree at every step.
    for i in range(n):
        for k in range(n):
            problem += agree[i][k] >= mine_order[i][k] + his_order[i][k] - 1
    problem += pulp.lpSum(agree[i][k] for i in range(n) for k in range(n)) <= n - 1

    # The chain from my age ends at his age, and the chain from his age ends at mine.
    problem += from_mine[0] == m
    problem += from_mine[n] == h
    problem += from_his[0] == h
    problem += from_his[n] == m

    # At each step, the operation applied there turns the value before it into the value after.
    # Where an operation is not applied, its equation is relaxed by its largest possible size.
    for values, order in ((from_mine, mine_order), (from_his, his_order)):
        for i in range(n):
            for k, (a, b, c) in enumerate(operations):
                low, high = span(a, b, c)
                expression = a * values[i + 1] + b * values[i] + c
                problem += expression <= high * (1 - order[i][k])
                problem += expression >= low * (1 - order[i][k])

    return problem, {"m": m, "h": h}


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
