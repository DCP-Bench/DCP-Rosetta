# session3_kidney_exchange: a Z3 (Python) model from DCP Rosetta.
# Download the `session3_kidney_exchange.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_kidney_exchange.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python session3_kidney_exchange.py session3_kidney_exchange.json

import z3


def create_model(instance):
    """People on a hospital waiting list for a kidney can donate to some of the
    others. Maximize the number of people who receive a kidney: anyone who gives a
    kidney must receive one, and nobody receives more than one."""
    num_people = instance["num_people"]  # the number of people on the waiting list
    compatible = instance["compatible"]  # compatible[i]: the people (numbered from 1) that person i can donate to

    # transplants[i][j] is true when person i donates a kidney to person j.
    transplants = [[z3.Bool(f"transplant_{i}_{j}") for j in range(num_people)] for i in range(num_people)]

    solver = z3.Optimize()
    for i in range(num_people):
        # gives: the number of kidneys person i donates.
        gives = z3.Sum([z3.If(transplants[i][j], 1, 0) for j in range(num_people)])
        # receives: the number of kidneys person i receives.
        receives = z3.Sum([z3.If(transplants[k][i], 1, 0) for k in range(num_people)])

        # Nobody gives more than one kidney, and nobody receives more than one.
        solver.add(gives <= 1, receives <= 1)

        # Anyone who gives a kidney must receive one.
        solver.add(gives <= receives)

        # A kidney goes only to a compatible person.
        for j in range(num_people):
            if j + 1 not in compatible[i]:
                solver.add(z3.Not(transplants[i][j]))

    # The number of transplants, which is the number of people who receive a kidney.
    objective = z3.Sum([z3.If(transplants[i][j], 1, 0) for i in range(num_people) for j in range(num_people)])

    solver.maximize(objective)

    return solver, {"transplants": transplants}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
