# csplib_084_hadamard_matrix: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_084_hadamard_matrix.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_084_hadamard_matrix.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_084_hadamard_matrix.py csplib_084_hadamard_matrix.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Find two sequences a and b of odd length l, with entries -1 or +1, that each
    sum to 1 and whose periodic autocorrelations add up to -2 at every shift
    s = 1, ..., (l-1)/2 (a Legendre pair, which gives a Hadamard matrix)."""
    l = instance["l"]                 # the length of each sequence, an odd positive integer
    n_shifts = (l - 1) // 2           # the number of shifts that are constrained

    model = cp_model.CpModel()

    def sequence(name):
        """The entries of one sequence of length l, each -1 or +1."""
        # plus[i] is true when entry i is +1
        plus = [model.new_bool_var(f"{name}_plus_{i}") for i in range(l)]
        # entry[i] is the value of entry i
        entry = [
            model.new_int_var_from_domain(cp_model.Domain.from_values([-1, 1]), f"{name}_{i}")
            for i in range(l)
        ]
        # Each entry is +1 where plus is true and -1 elsewhere.
        for i in range(l):
            model.add(entry[i] == 2 * plus[i] - 1)
        return plus, entry

    def paf(name, plus, s):
        """The periodic autocorrelation of a sequence at shift s, with the index i + s
        taken modulo l."""
        # agree[i] is true when entries i and i + s (mod l) are equal
        agree = []
        for i in range(l):
            same = model.new_bool_var(f"{name}_same_{s}_{i}")
            model.add(plus[i] == plus[(i + s) % l]).only_enforce_if(same)
            model.add(plus[i] != plus[(i + s) % l]).only_enforce_if(~same)
            agree.append(same)
        # an equal pair contributes +1 and an unequal pair -1
        return 2 * sum(agree) - l

    plus_a, a = sequence("a")
    plus_b, b = sequence("b")

    # Each sequence sums to 1.
    model.add(sum(a) == 1)
    model.add(sum(b) == 1)

    # At every shift the two autocorrelations add up to -2.
    for s in range(1, n_shifts + 1):
        model.add(paf("a", plus_a, s) + paf("b", plus_b, s) == -2)

    return model, {"a": a, "b": b}


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
