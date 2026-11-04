# session3_people_in_a_room: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_people_in_a_room.html
# Run it (after `pip install pulp numpy`) with:
#   python session3_people_in_a_room.py

import pulp


def create_model(instance):
    """People enter a room one at a time, some male and some female. Find an
    order of entry in which the ratio of females to males in the room is never
    more than 7/3."""
    total_people = 13  # the people entering the room
    num_males = 4      # the males among them

    problem = pulp.LpProblem("room", pulp.LpMinimize)

    # sequence[i] is 1 when the i-th person to enter is female, and 0 when male
    sequence = [pulp.LpVariable(f"s{i}", cat="Binary") for i in range(total_people)]

    # Exactly num_males of the people are male.
    problem += pulp.lpSum(sequence) == total_people - num_males

    # Over the first i people to enter, with F females and i - F males, 3F <= 7(i - F),
    # which is 10F <= 7i. Before anyone enters there is no ratio, so the check starts at the first person.
    for i in range(1, total_people):
        problem += 10 * pulp.lpSum(sequence[:i]) <= 7 * i

    return problem, {"sequence": sequence}


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
