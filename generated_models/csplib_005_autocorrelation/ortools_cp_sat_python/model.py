# csplib_005_autocorrelation: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_005_autocorrelation.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_005_autocorrelation.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_005_autocorrelation.py csplib_005_autocorrelation.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Low autocorrelation binary sequences: choose a sequence of n values, each +1 or -1,
    that minimises the sum of the squared periodic autocorrelations
    C_k = sum_i S_i * S_((i+k) mod n), for k = 1 to n-1."""
    n = instance["n"]  # the length of the sequence

    model = cp_model.CpModel()

    # plus[i] is true when the bit S_i is +1 and false when it is -1
    plus = [model.new_bool_var(f"plus_{i}") for i in range(n)]
    # sequence[i] is the bit S_i, either -1 or +1
    sequence = [model.new_int_var_from_domain(cp_model.Domain.from_values([-1, 1]), f"sequence_{i}")
                for i in range(n)]

    # same[(i, j)] is true when S_i and S_j are equal.
    same = {}

    def product(i, j):
        """The product S_i * S_j, as +1 or -1."""
        key = (min(i, j), max(i, j))
        if key not in same:
            lit = model.new_bool_var(f"same_{key[0]}_{key[1]}")
            model.add(plus[key[0]] == plus[key[1]]).only_enforce_if(lit)
            model.add(plus[key[0]] != plus[key[1]]).only_enforce_if(~lit)
            same[key] = lit
        return 2 * same[key] - 1

    # The bit S_i is +1 exactly when plus[i] is true.
    for i in range(n):
        model.add(sequence[i] == 2 * plus[i] - 1)

    # squares[k-1] is the square of C_k, the periodic autocorrelation at shift k.
    squares = []
    for k in range(1, n):
        correlation = model.new_int_var(-n, n, f"C_{k}")
        model.add(correlation == sum(product(i, (i + k) % n) for i in range(n)))
        square = model.new_int_var(0, n * n, f"C_{k}_squared")
        model.add_multiplication_equality(square, [correlation, correlation])
        squares.append(square)

    # energy E is the sum of the squared autocorrelations C_1 to C_(n-1)
    energy = model.new_int_var(0, (n - 1) * n * n, "energy")
    model.add(energy == sum(squares))

    # The objective is to minimise the energy.
    model.minimize(energy)

    return model, {"sequence": sequence}


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
