# session3_kidney_exchange: a PuLP (Python) model from DCP Rosetta.
# Download the `session3_kidney_exchange.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_kidney_exchange.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python session3_kidney_exchange.py session3_kidney_exchange.json

import pulp


def create_model(instance):
    """People on a hospital waiting list for a kidney can donate to some of the
    others, as given by a compatibility list. Maximize the number of people who
    receive a kidney: anyone who gives a kidney must receive one, and nobody
    receives more than one."""
    num_people = instance["num_people"]  # the number of people on the waiting list
    compatible = instance["compatible"]  # compatible[i]: the people that person i can donate to, numbered 1 to num_people
    people = range(num_people)

    problem = pulp.LpProblem("kidney_exchange", pulp.LpMaximize)

    # donates[i][j] is 1 when person i donates a kidney to person j, and 0 when not
    donates = [[pulp.LpVariable(f"t_{i}_{j}", cat="Binary") for j in people] for i in people]

    for i in people:
        gives = pulp.lpSum(donates[i])                        # the kidneys person i donates
        receives = pulp.lpSum(donates[k][i] for k in people)  # the kidneys person i receives
        # Nobody gives more than one kidney, and nobody receives more than one.
        problem += gives <= 1
        problem += receives <= 1
        # Anyone who gives a kidney must receive one.
        problem += gives <= receives
        # Donations go only to compatible people.
        for j in people:
            if j + 1 not in compatible[i]:
                problem += donates[i][j] == 0

    # The number of kidneys given, which is the number of people receiving one.
    problem += pulp.lpSum(donates[i][j] for i in people for j in people)

    return problem, {"transplants": donates}


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
