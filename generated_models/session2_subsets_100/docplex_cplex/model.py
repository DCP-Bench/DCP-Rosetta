# session2_subsets_100: a CPLEX (Python) model from DCP Rosetta.
# Download the `session2_subsets_100.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subsets_100.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python session2_subsets_100.py session2_subsets_100.json

from docplex.mp.model import Model


def create_model(instance):
    """Find two disjoint non-empty subsets S and T of the set A of different integers such that the
    sum of the elements in S equals the sum of the elements in T. S and T need not cover A."""
    A = instance["A"]  # A[i]: the i-th integer of the set
    n = len(A)

    model = Model("subsets_100")

    # in_S[i] is 1 when element i of A is in S, and in_T[i] is 1 when it is in T
    in_S = model.binary_var_list(n, name="in_S")
    in_T = model.binary_var_list(n, name="in_T")

    # The elements of S add up to the same sum as those of T.
    model.add_constraint(model.dot(in_S, A) == model.dot(in_T, A), ctname="equal_sums")

    # S and T are disjoint: no element is in both.
    model.add_constraints(in_S[i] + in_T[i] <= 1 for i in range(n))

    # S and T are non-empty.
    model.add_constraint(model.sum(in_S) >= 1, ctname="S_nonempty")
    model.add_constraint(model.sum(in_T) >= 1, ctname="T_nonempty")

    return model, {"in_S": in_S, "in_T": in_T}


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
