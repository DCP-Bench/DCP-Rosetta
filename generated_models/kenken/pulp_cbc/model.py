# kenken: a PuLP (Python) model from DCP Rosetta.
# Download the `kenken.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kenken.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python kenken.py kenken.json

import pulp


def create_model(instance):
    """Fill an n by n grid with the digits 1 to n so that every row and every column holds
    each digit once, and every cage reaches its target. Digits may repeat within a cage."""
    n = instance["n"]            # the grid is n by n, with digits 1 to n
    cages = instance["problem"]  # the cages: each one a target and the cells it covers

    problem = pulp.LpProblem("kenken", pulp.LpMinimize)

    # put[r][c][v] is 1 when the cell in row r, column c holds the digit v + 1, else 0
    put = pulp.LpVariable.dicts("put", (range(n), range(n), range(n)), cat="Binary")
    # x[r][c] is the digit in the cell in row r, column c
    x = [[pulp.LpVariable(f"x_{r}_{c}", 1, n, cat="Integer") for c in range(n)]
         for r in range(n)]

    # each cell holds exactly one digit, and that digit is its value in x
    for r in range(n):
        for c in range(n):
            problem += pulp.lpSum(put[r][c][v] for v in range(n)) == 1
            problem += x[r][c] == pulp.lpSum((v + 1) * put[r][c][v] for v in range(n))

    # each digit appears once in every row
    for v in range(n):
        for r in range(n):
            problem += pulp.lpSum(put[r][c][v] for c in range(n)) == 1

    # each digit appears once in every column
    for v in range(n):
        for c in range(n):
            problem += pulp.lpSum(put[r][c][v] for r in range(n)) == 1

    # The primes up to n are the only prime factors of the digits 1 to n. So a product of
    # digits equals a target exactly when each prime divides both the same number of times.
    primes = [p for p in range(2, n + 1) if all(p % q for q in range(2, p))]

    def exponent(p, number):
        """how many times the prime p divides number"""
        count = 0
        while number % p == 0:
            number //= p
            count += 1
        return count

    for k, (target, cells) in enumerate(cages):
        cells = [(r - 1, c - 1) for r, c in cells]

        if len(cells) == 1:
            # a single-cell cage: its digit is the target
            (r, c), = cells
            problem += x[r][c] == target

        elif len(cells) == 2:
            # The two digits a and b of the cage must give the target by a + b, a * b,
            # a - b, b - a, a / b or b / a. pair[(u, v)] is 1 when a is u and b is v, for
            # the pairs that give the target.
            (ra, ca), (rb, cb) = cells
            allowed = [(u, v) for u in range(1, n + 1) for v in range(1, n + 1)
                       if u + v == target or u * v == target or u * target == v
                       or v * target == u or u - v == target or v - u == target]
            pair = {uv: pulp.LpVariable(f"pair_{k}_{uv[0]}_{uv[1]}", 0, 1) for uv in allowed}
            # the first cell holds u exactly when one allowed pair starts with u
            for u in range(1, n + 1):
                problem += pulp.lpSum(pair[(u, v)] for v in range(1, n + 1)
                                      if (u, v) in pair) == put[ra][ca][u - 1]
            # the second cell holds v exactly when one allowed pair ends with v
            for v in range(1, n + 1):
                problem += pulp.lpSum(pair[(u, v)] for u in range(1, n + 1)
                                      if (u, v) in pair) == put[rb][cb][v - 1]

        else:
            # The cage reaches the target by the sum of its digits, or by their product.
            # by_sum is 1 when it does by the sum, and by_product is 1 when it does by the product.
            size = len(cells)  # the number of cells in the cage
            by_sum = pulp.LpVariable(f"by_sum_{k}", cat="Binary")
            by_product = pulp.LpVariable(f"by_product_{k}", cat="Binary")
            problem += by_sum + by_product >= 1

            # The digits add up to the target when the cage reaches it by sum. The sum of
            # the digits lies between size and size * n, so when the cage does not reach the
            # target by sum, the constraint is relaxed by the distance to those ends.
            total = pulp.lpSum(x[r][c] for r, c in cells)
            problem += total - target <= (size * n - target) * (1 - by_sum)
            problem += total - target >= (size - target) * (1 - by_sum)

            # rest is the target with every prime up to n divided out. It is 1 when the
            # target is a product of digits; otherwise the product option is off.
            rest = target
            for p in primes:
                while rest % p == 0:
                    rest //= p
            if rest != 1:
                problem += by_product == 0
            else:
                # For each prime, the times it divides the digits of the cage add up to the
                # times it divides the target. When the cage does not reach the target by
                # product, the constraint is relaxed by the distance to the ends of its range.
                for p in primes:
                    exp_total = pulp.lpSum(exponent(p, v + 1) * put[r][c][v]
                                           for r, c in cells for v in range(n))
                    wanted = exponent(p, target)
                    most = size * max(exponent(p, v) for v in range(1, n + 1))
                    problem += exp_total - wanted <= (most - wanted) * (1 - by_product)
                    problem += exp_total - wanted >= (0 - wanted) * (1 - by_product)

    return problem, {"x": x}


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
