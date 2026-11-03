# divisible_by_1_through_9: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/divisible_by_1_through_9.html
# Run it (after `pip install pulp numpy`) with:
#   python divisible_by_1_through_9.py

import pulp


def create_model(instance):
    """Find a 10-digit number that uses each digit 0 to 9 exactly once, where the
    number formed by its first n digits is divisible by n, for n = 1 to 10."""
    problem = pulp.LpProblem("divisible_by_1_through_9", pulp.LpMinimize)

    # The puzzle states its own length, so the instance holds no data.
    length = 10
    places = range(length)
    digit_values = range(10)

    # is_digit[i][v] is 1 if the digit at place i (from the left) is v.
    is_digit = [[pulp.LpVariable(f"is_digit_{i}_{v}", cat="Binary") for v in digit_values]
                for i in places]
    # digits[i] is the digit at place i, read from left to right.
    digits = [pulp.lpSum(v * is_digit[i][v] for v in digit_values) for i in places]

    # Every place holds one digit.
    for i in places:
        problem += pulp.lpSum(is_digit[i]) == 1

    # Each of the digits 0 to 9 is used exactly once.
    for v in digit_values:
        problem += pulp.lpSum(is_digit[i][v] for i in places) == 1

    # The number formed by the first i + 1 digits is divisible by i + 1. Only its remainder
    # matters, so each digit is weighted by 10^(i - j) mod (i + 1) rather than 10^(i - j);
    # this keeps every coefficient small instead of reaching 10^9, which a floating-point
    # solver cannot hold exactly. The weighted sum is then a multiple of i + 1.
    for i in places:
        divisor = i + 1
        weights = [pow(10, i - j, divisor) for j in range(i + 1)]
        largest = sum(w * 9 for w in weights)
        multiple = pulp.LpVariable(f"multiple_{i}", 0, largest // divisor, cat="Integer")
        problem += pulp.lpSum(w * digits[j] for j, w in enumerate(weights)) == divisor * multiple

    return problem, {"digits": digits}


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
