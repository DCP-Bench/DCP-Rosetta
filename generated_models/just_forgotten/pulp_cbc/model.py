# just_forgotten: a PuLP (Python) model from DCP Rosetta.
# Download the `just_forgotten.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/just_forgotten.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python just_forgotten.py just_forgotten.json

import pulp


def create_model(instance):
    """Joe forgot his bank account number. It uses each digit from 0 to n_digits - 1 once.
    In each set of digits he tried, a given number of digits are in their correct position.
    Find the account number."""
    sets = instance["sets"]  # sets[k][i]: the digit in position i of the k-th set Joe tried
    num_correct = instance["num_correct_digits"]  # how many digits of each set are in their correct position
    n_digits = len(sets[0])

    problem = pulp.LpProblem("just_forgotten", pulp.LpMinimize)

    # digit_at[i][d] is 1 when digit d is in position i of the account number, and 0 when not.
    digit_at = [[pulp.LpVariable(f"digit_at_{i}_{d}", cat="Binary") for d in range(n_digits)]
                for i in range(n_digits)]

    # Each position holds one digit.
    for i in range(n_digits):
        problem += pulp.lpSum(digit_at[i]) == 1

    # Each digit is in one position.
    for d in range(n_digits):
        problem += pulp.lpSum(digit_at[i][d] for i in range(n_digits)) == 1

    # Each set has exactly num_correct digits in their correct position.
    for guess in sets:
        problem += pulp.lpSum(digit_at[i][guess[i]] for i in range(n_digits)) == num_correct

    # x[i] is the digit in position i of the account number.
    x = [pulp.LpVariable(f"x_{i}", 0, n_digits - 1, cat="Integer") for i in range(n_digits)]

    # The digit in each position is the one that digit_at places there.
    for i in range(n_digits):
        problem += x[i] == pulp.lpSum(d * digit_at[i][d] for d in range(n_digits))

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
