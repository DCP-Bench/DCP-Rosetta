# session1_guards_and_apples: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `session1_guards_and_apples.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_guards_and_apples.html
# Then run it on the first instance (after `pip install ortools`):
#   python session1_guards_and_apples.py session1_guards_and_apples.json

from ortools.sat.python import cp_model


def create_model(instance):
    """A boy passes through a number of gates to give an apple to a girl. He
    bribes each guard with half of his apples plus one, always a whole number
    of apples, and has none left after giving the girl her apple."""
    num_gates = instance["num_gates"]  # the number of gates, each with a guard

    model = cp_model.CpModel()

    # apples[i] is the number of apples the boy has before gate i. The last entry
    # is the number he has after the last gate.
    apples = [model.new_int_var(0, 100, f"apples_{i}") for i in range(num_gates)]
    # The one apple left over after the last gate is the girl's.
    apples.append(model.new_int_var(1, 1, f"apples_{num_gates}"))

    # Before each gate he had twice what remains after it, plus 2.
    for i in range(num_gates):
        model.add(apples[i] == 2 * (apples[i + 1] + 1))

    return model, {"apples": apples}


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
