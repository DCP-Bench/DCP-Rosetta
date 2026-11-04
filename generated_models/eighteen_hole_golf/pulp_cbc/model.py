# eighteen_hole_golf: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/eighteen_hole_golf.html
# Run it (after `pip install pulp numpy`) with:
#   python eighteen_hole_golf.py

import pulp


def create_model(instance):
    """A golf course has 18 holes, each of length 3, 4 or 5, and the total length
    of the course is 72. Find the length of each hole."""
    n_holes = 18        # the course has 18 holes
    total_length = 72   # the lengths of all holes add up to 72

    problem = pulp.LpProblem("golf", pulp.LpMinimize)

    # holes[i] is the length of hole i, one of 3, 4 or 5
    holes = [pulp.LpVariable(f"hole_{i}", 3, 5, cat="Integer") for i in range(n_holes)]

    # The hole lengths add up to the length of the course.
    problem += pulp.lpSum(holes) == total_length

    # There is no objective: any course that meets the rules is an answer.
    return problem, {"holes": holes}


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
