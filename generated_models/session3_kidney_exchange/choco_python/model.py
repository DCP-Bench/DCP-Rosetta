# session3_kidney_exchange: a Choco-solver (Python) model from DCP Rosetta.
# Download the `session3_kidney_exchange.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_kidney_exchange.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python session3_kidney_exchange.py session3_kidney_exchange.json

from pychoco.model import Model


def create_model(instance):
    """People on a hospital waiting list for a kidney can donate to some of the
    others, as given by a directed compatibility graph. Maximize the number of
    people who receive a kidney: anyone who gives a kidney must receive one, and
    nobody receives more than one."""
    n_people = instance["num_people"]    # the number of people on the waiting list
    compatible = instance["compatible"]  # compatible[i]: the people that person i can donate a kidney to

    model = Model()

    # transplants[i][j] is 1 when person i donates a kidney to person j. A donation
    # to someone outside the compatibility list is fixed to 0.
    transplants = [[model.intvar(0, 1 if j + 1 in compatible[i] else 0, name=f"transplants_{i}_{j}")
                    for j in range(n_people)] for i in range(n_people)]

    for i in range(n_people):
        # the kidneys person i donates, and the kidneys person i receives
        gives = [transplants[i][j] for j in range(n_people) if j + 1 in compatible[i]]
        receives = [transplants[j][i] for j in range(n_people) if i + 1 in compatible[j]]
        # Nobody gives more than one kidney, and nobody receives more than one.
        if gives:
            model.sum(gives, "<=", 1).post()
        if receives:
            model.sum(receives, "<=", 1).post()
        # Anyone who gives a kidney must receive one.
        if gives:
            model.scalar(gives + receives, [1] * len(gives) + [-1] * len(receives), "<=", 0).post()

    # the number of kidneys given, which is the number of people receiving one
    n_transplants = model.intvar(0, n_people, name="n_transplants")
    donations = [transplants[i][j] for i in range(n_people) for j in range(n_people) if j + 1 in compatible[i]]
    model.sum(donations, "=", n_transplants).post()

    return model, {"transplants": transplants}, {"objective": n_transplants, "maximize": True}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
