# session1_bank_card: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_bank_card.html
# Run it (after `pip install pulp numpy`) with:
#   python session1_bank_card.py

import pulp


def create_model(instance):
    """A bank card has a four-digit PIN abcd: no two digits are the same, the
    two-digit number cd is 3 times ab, and da is 2 times bc."""
    names = ["a", "b", "c", "d"]  # the four PIN digits, in order
    digits = range(10)            # the digit values 0 to 9

    problem = pulp.LpProblem("bank_card", pulp.LpMinimize)

    # is_digit[x][v] is 1 when PIN digit x is v, and 0 when not
    is_digit = {x: [pulp.LpVariable(f"is_{x}_{v}", cat="Binary") for v in digits] for x in names}

    # Each PIN digit is exactly one digit.
    for x in names:
        problem += pulp.lpSum(is_digit[x]) == 1

    # No two digits are the same.
    for v in digits:
        problem += pulp.lpSum(is_digit[x][v] for x in names) <= 1

    # The value of each PIN digit.
    a, b, c, d = (pulp.lpSum(v * is_digit[x][v] for v in digits) for x in names)

    # The two-digit number cd is 3 times the two-digit number ab.
    problem += 10 * c + d == 3 * (10 * a + b)

    # The two-digit number da is 2 times the two-digit number bc.
    problem += 10 * d + a == 2 * (10 * b + c)

    # No objective: any PIN that fits the clues is an answer.
    return problem, {"a": a, "b": b, "c": c, "d": d}


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
