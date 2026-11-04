# csplib_019_magic_squares_and_sequences: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_019_magic_squares_and_sequences.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_019_magic_squares_and_sequences.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_019_magic_squares_and_sequences.py csplib_019_magic_squares_and_sequences.json

import pulp


def create_model(instance):
    """A magic sequence of length n is a sequence of integers x_0, ..., x_{n-1}
    between 0 and n-1 such that, for every i, the number i occurs exactly x_i times
    in the sequence."""
    n_positions = instance["n"]  # the length of the sequence; its values are 0 to n-1

    problem = pulp.LpProblem("magic_sequence", pulp.LpMinimize)

    # holds[j][v] is 1 when position j of the sequence holds the value v
    holds = [[pulp.LpVariable(f"holds_{j}_{v}", cat="Binary") for v in range(n_positions)]
             for j in range(n_positions)]

    # x[j] is the value at position j, and also how often the number j occurs
    x = [pulp.LpVariable(f"x_{j}", 0, n_positions - 1, cat="Integer") for j in range(n_positions)]

    # Each position holds exactly one value, and x[j] is that value.
    for j in range(n_positions):
        problem += pulp.lpSum(holds[j]) == 1
        problem += x[j] == pulp.lpSum(v * holds[j][v] for v in range(n_positions))

    # The number i occurs exactly x[i] times in the sequence.
    for i in range(n_positions):
        problem += x[i] == pulp.lpSum(holds[j][i] for j in range(n_positions))

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
