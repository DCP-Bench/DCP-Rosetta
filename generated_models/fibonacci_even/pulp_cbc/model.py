# fibonacci_even: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fibonacci_even.html
# Run it (after `pip install pulp numpy`) with:
#   python fibonacci_even.py

import pulp


def create_model(instance):
    """Each new term of the Fibonacci sequence is the sum of the two before it, starting from
    1 and 2. Find the sum of the even-valued terms that do not exceed four million."""
    problem = pulp.LpProblem("fibonacci_even", pulp.LpMinimize)

    n = 35               # terms f[0] to f[n] are generated
    term_top = 10 ** 7   # bound on every term, above f[35] = 9227465
    limit = 4000000      # four million, the largest term that counts
    res_top = 10 ** 8    # bound on the sum
    terms = range(1, n + 1)

    # f[i] is the i-th term of the sequence 0, 1, 1, 2, 3, 5, ...; the puzzle's terms
    # 1, 2, 3, 5, ... are f[2], f[3], ...
    f = [pulp.LpVariable(f"f_{i}", 0, term_top, cat="Integer") for i in range(n + 1)]
    # odd[i] is 1 when f[i] is odd.
    odd = [pulp.LpVariable(f"odd_{i}", cat="Binary") for i in range(n + 1)]
    # small[i] is 1 exactly when f[i] is below four million.
    small = {i: pulp.LpVariable(f"small_{i}", cat="Binary") for i in terms}
    # x[i] is 1 exactly when f[i] is even and below four million.
    x = {i: pulp.LpVariable(f"x_{i}", cat="Binary") for i in terms}
    # picked[i] is x[i] * f[i], linearized.
    picked = {i: pulp.LpVariable(f"picked_{i}", 0, limit - 1, cat="Integer") for i in terms}
    # res is the sum of the terms selected by x.
    res = pulp.LpVariable("res", 0, res_top, cat="Integer")

    # The sequence starts 0, 1, 1 and each later term is the sum of the two before it.
    problem += f[0] == 0
    problem += f[1] == 1
    problem += f[2] == 1
    for i in range(3, n + 1):
        problem += f[i] == f[i - 1] + f[i - 2]

    # odd[i] is 1 if f[i] is odd: f[i] = 2 * half + odd[i].
    for i in range(n + 1):
        half = pulp.LpVariable(f"half_{i}", 0, term_top // 2, cat="Integer")
        problem += f[i] == 2 * half + odd[i]
    # Implied by the recurrence, stated so the solver needs no search to find parities: a
    # term is odd exactly when one of the two terms before it is (odd = xor of those two).
    for i in range(3, n + 1):
        a, b, c = odd[i - 1], odd[i - 2], odd[i]
        problem += c <= a + b
        problem += c >= a - b
        problem += c >= b - a
        problem += c <= 2 - a - b

    # small[i] is 1 exactly when f[i] is below four million.
    for i in terms:
        problem += f[i] <= limit - 1 + (term_top - limit + 1) * (1 - small[i])
        problem += f[i] >= limit - limit * small[i]
    # Implied: from f[2] on the terms never decrease, so once a term reaches the limit
    # every later one does too.
    for i in range(3, n + 1):
        problem += small[i] <= small[i - 1]

    # x[i] is 1 exactly when f[i] is even and below four million.
    for i in terms:
        problem += x[i] <= small[i]
        problem += x[i] <= 1 - odd[i]
        problem += x[i] >= small[i] - odd[i]

    # picked[i] equals f[i] when x[i] is 1 and 0 otherwise. A selected term is below the
    # limit, so limit - 1 bounds picked[i]; term_top bounds the gap when x[i] is 0.
    for i in terms:
        problem += picked[i] <= (limit - 1) * x[i]
        problem += picked[i] <= f[i]
        problem += picked[i] >= f[i] - term_top * (1 - x[i])

    # res is the sum of the selected terms.
    problem += res == pulp.lpSum(picked.values())

    return problem, {"res": res}


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
