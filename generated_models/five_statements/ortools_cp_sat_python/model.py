# five_statements: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_statements.html
# Run it (after `pip install ortools`) with:
#   python five_statements.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Five statements:
    - Exactly one of these statements is false.
    - Exactly two of these statements are false.
    - Exactly three of these statements are false.
    - Exactly four of these statements are false.
    - Exactly five of these statements are false.
    Determine which of the statements are true."""
    n_statements = 5  # the number of statements

    model = cp_model.CpModel()

    # statements[i] is true when statement i + 1 is true
    statements = [model.new_bool_var(f"statements_{i}") for i in range(n_statements)]

    # The number of false statements
    n_false = sum(~s for s in statements)
    # Statement i says that exactly i + 1 statements are false.
    for i in range(n_statements):
        model.add(n_false == i + 1).only_enforce_if(statements[i])
        model.add(n_false != i + 1).only_enforce_if(~statements[i])

    return model, {"statements": statements}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
