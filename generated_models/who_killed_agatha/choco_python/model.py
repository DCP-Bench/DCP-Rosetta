# who_killed_agatha: a Choco-solver (Python) model from DCP Rosetta.
# Download the `who_killed_agatha.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/who_killed_agatha.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python who_killed_agatha.py who_killed_agatha.json

from pychoco.model import Model


def create_model(instance):
    """Someone in Dreadsbury Mansion killed Aunt Agatha. Agatha, the butler and
    Charles are the only residents. From the clues about who hates whom and who
    is richer than whom, find out who killed Agatha."""
    names = instance["names"]  # names[i]: the name of resident i
    n_residents = len(names)   # the residents, the only people in the mansion
    agatha = names.index("Agatha herself")  # the resident who was killed
    butler = names.index("the butler")
    charles = names.index("Charles")

    model = Model()

    # The killer is one of the residents.
    killer = model.intvar(0, n_residents - 1, name="killer")
    # hates[i][j] is true when resident i hates resident j
    hates = [[model.boolvar(name=f"hates_{i}_{j}") for j in range(n_residents)]
             for i in range(n_residents)]
    # richer[i][j] is true when resident i is richer than resident j
    richer = [[model.boolvar(name=f"richer_{i}_{j}") for j in range(n_residents)]
              for i in range(n_residents)]
    # The values 1 (true) and 0 (false), for the element constraints below.
    one = model.intvar(1, 1, name="one")
    zero = model.intvar(0, 0, name="zero")

    # A killer always hates his victim, and is no richer than his victim.
    model.element(one, [hates[i][agatha] for i in range(n_residents)], killer).post()
    model.element(zero, [richer[i][agatha] for i in range(n_residents)], killer).post()

    # Nobody is richer than himself, and of two different residents exactly one is richer.
    for i in range(n_residents):
        model.arithm(richer[i][i], "=", 0).post()
        for j in range(i + 1, n_residents):
            model.arithm(richer[i][j], "+", richer[j][i], "=", 1).post()

    # Charles hates no one that Agatha hates.
    for i in range(n_residents):
        model.arithm(hates[agatha][i], "+", hates[charles][i], "<=", 1).post()

    # Agatha hates everybody except the butler.
    for i in range(n_residents):
        model.arithm(hates[agatha][i], "=", 0 if i == butler else 1).post()

    # The butler hates everyone not richer than Agatha.
    for i in range(n_residents):
        model.arithm(richer[i][agatha], "+", hates[butler][i], ">=", 1).post()

    # The butler hates everyone whom Agatha hates.
    for i in range(n_residents):
        model.arithm(hates[agatha][i], "<=", hates[butler][i]).post()

    # Nobody hates everyone.
    for i in range(n_residents):
        model.sum(hates[i], "<=", n_residents - 1).post()

    return model, {"killer": killer}, None


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
