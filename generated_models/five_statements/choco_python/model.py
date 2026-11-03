# five_statements: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_statements.html
# Run it (after `pip install pychoco numpy`) with:
#   python five_statements.py

from pychoco.model import Model


def create_model(instance):
    """Five statements say that exactly one, exactly two, exactly three,
    exactly four and exactly five of these statements are false. Determine
    which of them are true."""
    n_statements = 5  # the number of statements

    model = Model()

    # statements[i] is true when statement i + 1 is true
    statements = [model.boolvar(name=f"statement_{i}") for i in range(n_statements)]

    # The number of false statements is what is left after counting the true ones.
    n_false = model.intvar(0, n_statements, name="n_false")
    model.sum(statements + [n_false], "=", n_statements).post()

    # Statement i + 1 is true exactly when exactly i + 1 statements are false.
    for i in range(n_statements):
        model.arithm(n_false, "=", i + 1).reify_with(statements[i])

    return model, {"statements": statements}, None


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
