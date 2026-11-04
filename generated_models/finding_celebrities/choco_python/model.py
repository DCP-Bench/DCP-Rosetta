# finding_celebrities: a Choco-solver (Python) model from DCP Rosetta.
# Download the `finding_celebrities.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/finding_celebrities.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python finding_celebrities.py finding_celebrities.json

from pychoco.model import Model


def create_model(instance):
    """At a party, a celebrity is a guest whom everybody knows and who knows
    only celebrities. Find the celebrities; at least one is present."""
    graph = instance["graph"]  # graph[i][j] is 1 when guest i knows guest j
    n_guests = len(graph)      # the number of guests

    model = Model()

    # celebrities[i] is true when guest i is a celebrity
    celebrities = [model.boolvar(name=f"celebrities_{i}") for i in range(n_guests)]
    # n_celebrities is how many guests are celebrities
    n_celebrities = model.intvar(1, n_guests, name="n_celebrities")
    model.sum(celebrities, "=", n_celebrities).post()

    # A celebrity knows every other celebrity, so among the guests everybody knows,
    # a celebrity is exactly the guest who knows as many guests as there are celebrities.
    for i in range(n_guests):
        # whether everybody knows guest i
        known_by_everybody = sum(graph[j][i] for j in range(n_guests)) == n_guests
        # how many guests guest i knows
        n_known = sum(graph[i])
        if known_by_everybody:
            model.arithm(n_celebrities, "=", n_known).reify_with(celebrities[i])
        else:
            # A guest whom not everybody knows is no celebrity.
            model.arithm(celebrities[i], "=", 0).post()

    return model, {"celebrities": celebrities}, None


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
