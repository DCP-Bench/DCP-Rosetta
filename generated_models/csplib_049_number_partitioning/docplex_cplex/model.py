# csplib_049_number_partitioning: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_049_number_partitioning.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_049_number_partitioning.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_049_number_partitioning.py csplib_049_number_partitioning.json

from docplex.mp.model import Model


def create_model(instance):
    """Number partitioning: split 1..n into two sets of equal size with equal sums and equal sums of squares."""
    n = instance["n"]  # the numbers 1..n are split into two sets A and B
    half = n // 2  # the size of each set (the two sets have the same cardinality)
    values = range(1, n + 1)
    slots = range(n)  # slots 0..half-1 are the members of A, the rest those of B
    in_A = range(half)
    in_B = range(half, n)

    model = Model("number_partitioning")

    # holds[s, v] is 1 when slot s holds number v. Each slot holds one number and
    # each number is in one slot, so A and B partition 1..n with n/2 each.
    holds = model.binary_var_matrix(slots, values, name="holds")
    model.add_constraints(model.sum(holds[s, v] for v in values) == 1 for s in slots)
    model.add_constraints(model.sum(holds[s, v] for s in slots) == 1 for v in values)

    def total(set_slots, power):  # sum over a set of its numbers (power 1) or of their squares (power 2)
        return model.sum(v ** power * holds[s, v] for s in set_slots for v in values)

    # The numbers in A add up to the same sum as those in B.
    model.add_constraint(total(in_A, 1) == total(in_B, 1), ctname="sums")

    # So do their squares; with one-hot slots a square is a constant coefficient.
    model.add_constraint(total(in_A, 2) == total(in_B, 2), ctname="squares")

    # The numbers of set A and of set B, read back from the slots.
    def members(slot_range):
        return [model.sum(v * holds[s, v] for v in values) for s in slot_range]

    return model, {"A": members(in_A), "B": members(in_B)}


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
