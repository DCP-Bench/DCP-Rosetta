# session1_bank_card: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_bank_card.html
# Run it (after `pip install pychoco numpy`) with:
#   python session1_bank_card.py

from pychoco.model import Model


def create_model(instance):
    """A bank card has a four-digit PIN abcd: no two digits are the same, the
    two-digit number cd is 3 times ab, and da is 2 times bc."""
    model = Model()

    # The four digits of the PIN, a b c d
    digits = [model.intvar(0, 9, name=name) for name in "abcd"]
    a, b, c, d = digits

    # No two digits are the same.
    model.all_different(digits).post()

    # The two-digit number cd is 3 times the two-digit number ab.
    model.scalar([c, d, a, b], [10, 1, -30, -3], "=", 0).post()

    # The two-digit number da is 2 times the two-digit number bc.
    model.scalar([d, a, b, c], [10, 1, -20, -2], "=", 0).post()

    return model, {"a": a, "b": b, "c": c, "d": d}, None


if __name__ == "__main__":
    import numpy as np

    model, outputs, objective = create_model({})
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
