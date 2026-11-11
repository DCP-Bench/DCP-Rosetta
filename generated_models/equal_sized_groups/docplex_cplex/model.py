# equal_sized_groups: a CPLEX (Python) model from DCP Rosetta.
# Download the `equal_sized_groups.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/equal_sized_groups.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python equal_sized_groups.py equal_sized_groups.json

from docplex.mp.model import Model


def create_model(instance):
    """Equal-sized groups: split a sorted list into k groups at k - 1 break points, keeping equal values together, with sizes as close to n / k as possible."""
    a = instance["a"]  # the sorted list of elements
    k = instance["k"]  # the number of groups
    n = len(a)
    ideal = round(n / k)  # the ideal group size, round(N/K) as in the statement
    breaks = range(k - 1)

    # A break point j (1-based: the first j elements lie before it) may not
    # separate two equal values, so it can only sit where the value changes.
    allowed = [j for j in range(1, n) if a[j - 1] != a[j]]

    model = Model("equal_sized_groups")

    # at[p, j] is 1 when break point p is at position j. Choosing among the
    # allowed positions encodes "equal values stay in one group" directly,
    # instead of forbidding each of the many other positions one by one.
    at = model.binary_var_matrix(breaks, allowed, name="at")
    for p in breaks:
        model.add_constraint(model.sum(at[p, j] for j in allowed) == 1, ctname=f"one_position_{p}")
    x = [model.sum(j * at[p, j] for j in allowed) for p in breaks]

    # size[i] is the number of elements in group i; each group holds at least one element:
    # the first group ends at the first break point, each later one at the next,
    # and the last runs to the end of the list.
    size = model.integer_var_list(k, 1, n, name="size")
    model.add_constraint(size[0] == x[0], ctname="first_group")
    for i in range(1, k - 1):
        model.add_constraint(size[i] == x[i] - x[i - 1], ctname=f"group_{i}")
    model.add_constraint(size[k - 1] == n - x[k - 2], ctname="last_group")

    # error[i] is at least the distance of group i's size from the ideal size;
    # since the total is minimised, each is exactly that distance at the optimum.
    error = model.integer_var_list(k, 0, n, name="error")
    for i in range(k):
        model.add_constraint(error[i] >= size[i] - ideal, ctname=f"over_{i}")
        model.add_constraint(error[i] >= ideal - size[i], ctname=f"under_{i}")

    # Minimise the total error.
    total_error = model.sum(error)
    model.minimize(total_error)

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.parameters.mip.tolerances.mipgap = 0  # prove the optimum; the default stops within 0.01% of it
    solution = model.solve()

    if solution:  # a proven optimum
        print("Objective value:", round(solution.objective_value))

        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
