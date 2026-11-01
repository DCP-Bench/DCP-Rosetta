# send_more_money: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/send_more_money.html
# Run it (after `pip install pychoco numpy`) with:
#   python send_more_money.py

from pychoco.model import Model


def create_model(instance):
    """Cryptarithmetic puzzle: give each letter a different digit so that SEND + MORE =
    MONEY holds as a sum of decimal numbers, with no word starting with a zero."""
    model = Model()

    # digit[L]: the digit that letter L stands for. The first letter of SEND and of MORE is not zero.
    digit = {L: model.intvar(1 if L in "sm" else 0, 9, name=L) for L in "sendmory"}
    s, e, n, d, m, o, r, y = (digit[L] for L in "sendmory")

    # Different letters stand for different digits.
    model.all_different(list(digit.values())).post()

    # SEND + MORE - MONEY = 0, with the place values of each letter collected.
    # S: 1000; E: 100 + 1 - 10 = 91; N: 10 - 100 = -90; D: 1; M: 1000 - 10000 = -9000;
    # O: 100 - 1000 = -900; R: 10; Y: -1.
    model.scalar([s, e, n, d, m, o, r, y],
                 [1000, 91, -90, 1, -9000, -900, 10, -1], "=", 0).post()

    return model, digit, None


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
