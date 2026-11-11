# csplib_019_magic_squares_and_sequences: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_019_magic_squares_and_sequences.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_019_magic_squares_and_sequences.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_019_magic_squares_and_sequences.py csplib_019_magic_squares_and_sequences.json

from docplex.mp.model import Model


def create_model(instance):
    """Magic sequence of length n: integers x_0, ..., x_{n-1} between 0 and n-1 such that, for every i,
    the number i occurs exactly x_i times in the sequence."""
    n = instance["n"]  # length of the sequence; values run from 0 to n - 1

    model = Model("magic_sequence")

    # holds[i, v] is 1 when position i holds the value v.
    holds = model.binary_var_matrix(range(n), range(n), name="holds")

    # Every position holds exactly one value.
    model.add_constraints(model.sum(holds[i, v] for v in range(n)) == 1 for i in range(n))

    # x[i] is the value at position i, read back from the assignment.
    x = [model.sum(v * holds[i, v] for v in range(n)) for i in range(n)]

    # The number i occurs exactly x[i] times in the sequence: the positions that hold the
    # value i are counted through the assignment.
    model.add_constraints(x[i] == model.sum(holds[j, i] for j in range(n)) for i in range(n))

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
