# who_killed_agatha: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `who_killed_agatha.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/who_killed_agatha.html
# Then run it on the first instance (after `pip install ortools`):
#   python who_killed_agatha.py who_killed_agatha.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Someone in Dreadsbury Mansion killed Aunt Agatha. Agatha, the butler and
    Charles are the only residents. From the clues about who hates whom and who
    is richer than whom, find out who killed Agatha."""
    names = instance["names"]  # names[i]: the name of resident i
    n_residents = len(names)   # the number of residents

    # The indices of Agatha, the butler and Charles among the residents.
    agatha = names.index("Agatha herself")
    butler = names.index("the butler")
    charles = names.index("Charles")
    victim = agatha            # the resident who was killed

    model = cp_model.CpModel()

    # killer is the index of the resident who killed Agatha
    killer = model.new_int_var(0, n_residents - 1, "killer")
    # hates[i][j] is true when resident i hates resident j
    hates = [[model.new_bool_var(f"hates_{i}_{j}") for j in range(n_residents)] for i in range(n_residents)]
    # richer[i][j] is true when resident i is richer than resident j
    richer = [[model.new_bool_var(f"richer_{i}_{j}") for j in range(n_residents)] for i in range(n_residents)]

    # A killer always hates, and is no richer than, his victim.
    model.add_element(killer, [hates[i][victim] for i in range(n_residents)], 1)
    model.add_element(killer, [richer[i][victim] for i in range(n_residents)], 0)

    for i in range(n_residents):
        # Nobody is richer than himself.
        model.add(richer[i][i] == 0)
        # Of two different residents, exactly one is richer than the other.
        for j in range(i + 1, n_residents):
            model.add(richer[i][j] != richer[j][i])

        # Charles hates nobody that Agatha hates.
        model.add_implication(hates[agatha][i], ~hates[charles][i])
        # The butler hates everyone not richer than Agatha.
        model.add_implication(~richer[i][agatha], hates[butler][i])
        # The butler hates everyone whom Agatha hates.
        model.add_implication(hates[agatha][i], hates[butler][i])
        # Nobody hates everyone.
        model.add(sum(hates[i]) <= n_residents - 1)

    # Agatha hates everybody except the butler.
    model.add(hates[agatha][agatha] == 1)
    model.add(hates[agatha][charles] == 1)
    model.add(hates[agatha][butler] == 0)

    return model, {"killer": killer}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
