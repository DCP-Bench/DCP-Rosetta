# five_brigands: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_brigands.html
# Run it (after `pip install pychoco numpy`) with:
#   python five_brigands.py

from pychoco.model import Model


def create_model(instance):
    """Five Spanish brigands, Alfonso, Benito, Carlos, Diego and Esteban, have
    captured exactly 200 doubloons altogether. If Alfonso had twelve times as
    much, Benito three times as much, Carlos the same amount, Diego half as
    much and Esteban one third as much, they would still have 200 doubloons
    altogether. No brigand has less than one doubloon. How many has each?"""
    total = 200  # the doubloons the brigands have altogether

    model = Model()

    # The doubloons of Alfonso, Benito, Carlos, Diego and Esteban, at least one each.
    a, b, c, d, e = [model.intvar(1, total, name=name) for name in "ABCDE"]
    brigands = [a, b, c, d, e]

    # Together they have all the doubloons.
    model.sum(brigands, "=", total).post()

    # With the changed amounts they still have the total. Multiplied by 6 to
    # clear the halves and thirds: 72A + 18B + 6C + 3D + 2E = 6 * total.
    model.scalar(brigands, [72, 18, 6, 3, 2], "=", 6 * total).post()

    return model, {"A": a, "B": b, "C": c, "D": d, "E": e}, None


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
