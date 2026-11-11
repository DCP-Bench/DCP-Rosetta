# clock_triplets: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/clock_triplets.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python clock_triplets.py

from docplex.mp.model import Model


def create_model(instance):
    """Clock triplets: rearrange the numbers 1 to 12 on a clock face so that no three adjacent
    numbers sum to more than 21."""
    # The clock shows the numbers 1..n, and no three adjacent numbers may sum to more than limit.
    n = 12
    limit = 21
    positions = range(n)
    numbers = range(1, n + 1)

    model = Model("clock_triplets")

    # at[i, v] is 1 when position i shows number v. Every position shows one number and every
    # number appears once (all different).
    at = {(i, v): model.binary_var(name=f"at_{i}_{v}") for i in positions for v in numbers}
    model.add_constraints(model.sum(at[i, v] for v in numbers) == 1 for i in positions)
    model.add_constraints(model.sum(at[i, v] for i in positions) == 1 for v in numbers)

    # x[i] is the number at position i.
    x = [model.sum(v * at[i, v] for v in numbers) for i in positions]

    # No three adjacent numbers around the clock sum to more than the limit (x[-1] and x[-2]
    # are the last positions, which wrap round to position 0).
    model.add_constraints(x[i] + x[i - 1] + x[i - 2] <= limit for i in positions)

    return model, {"x": x}


if __name__ == "__main__":
    model, outputs = create_model({})
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
