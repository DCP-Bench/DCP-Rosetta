# four_numbers: a PuLP (Python) model from DCP Rosetta.
# Download the `four_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_numbers.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python four_numbers.py four_numbers.json

import pulp


def create_model(instance):
    """Given up to four distinct numbers from 1 to 10, find three numbers from 1 to 10
    such that every given number is a sum of some of the three."""
    numbers = instance["numbers"]  # the given numbers, each one to be a sum of some of the answer numbers
    n_numbers = len(numbers)
    n_values = 3  # how many numbers the answer holds
    largest = 10  # the largest number allowed in the answer

    problem = pulp.LpProblem("four_numbers", pulp.LpMinimize)

    # x[j] is the j-th answer number, from 1 to largest
    x = [pulp.LpVariable(f"x{j}", 1, largest, cat="Integer") for j in range(n_values)]

    # Each given number is the sum of some of the answer numbers.
    for i in range(n_numbers):
        # parts[j] is x[j] when x[j] is used in the sum for numbers[i], and 0 when not
        parts = []
        for j in range(n_values):
            # used[j] is 1 when x[j] is used in the sum for numbers[i], and 0 when not
            used = pulp.LpVariable(f"used_{i}_{j}", cat="Binary")
            part = pulp.LpVariable(f"part_{i}_{j}", 0, largest, cat="Integer")
            problem += part <= largest * used
            problem += part <= x[j]
            problem += part >= x[j] - largest * (1 - used)
            parts.append(part)
        problem += pulp.lpSum(parts) == numbers[i]

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
