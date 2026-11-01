# csplib_005_autocorrelation: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_005_autocorrelation.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_005_autocorrelation.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_005_autocorrelation.py csplib_005_autocorrelation.json

from pychoco.model import Model


def create_model(instance):
    """Low autocorrelation binary sequence: choose n_bits values, each +1 or -1, that minimise
    the sum of the squared periodic autocorrelations C_k, for k = 1 to n_bits - 1, where
    C_k is the sum over i of S_i * S_((i + k) mod n_bits)."""
    n_bits = instance["n"]  # the length of the sequence

    model = Model()

    # sequence[i] is the bit S_i, either -1 or +1
    sequence = [model.intvar([-1, 1], name=f"sequence_{i}") for i in range(n_bits)]

    # squares[k - 1] is the square of the autocorrelation C_k
    squares = [model.intvar(0, n_bits * n_bits, name=f"square_{k}") for k in range(1, n_bits)]

    # Each autocorrelation C_k is the sum of the products S_i * S_((i + k) mod n_bits).
    for k in range(1, n_bits):
        correlation = model.intvar(-n_bits, n_bits, name=f"correlation_{k}")

        # products[i] is the product S_i * S_((i + k) mod n_bits), which is +1 or -1
        products = [model.intvar([-1, 1], name=f"product_{k}_{i}") for i in range(n_bits)]
        for i in range(n_bits):
            model.times(sequence[i], sequence[(i + k) % n_bits], products[i]).post()
        model.sum(products, "=", correlation).post()

        model.square(squares[k - 1], correlation).post()

    # The energy is the sum of the squared autocorrelations, to be minimised.
    energy = model.intvar(0, (n_bits - 1) * n_bits * n_bits, name="energy")
    model.sum(squares, "=", energy).post()

    return model, {"sequence": sequence}, {"objective": energy, "maximize": False}


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
