# session3_farmer_and_cows: a CPLEX (Python) model from DCP Rosetta.
# Download the `session3_farmer_and_cows.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_farmer_and_cows.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python session3_farmer_and_cows.py session3_farmer_and_cows.json

from docplex.mp.model import Model


def create_model(instance):
    """A farmer has cows numbered 1 to num_cows, each giving as much milk as its number. He
    distributes them among his sons, each son getting the given number of cows, so that the
    total quantity of milk is the same for each son."""
    num_cows = instance["num_cows"]          # the number of cows
    num_sons = instance["num_sons"]          # the number of sons
    cows_per_son = instance["cows_per_son"]  # cows_per_son[s]: how many cows son s gets
    cows = range(num_cows)
    sons = range(num_sons)
    # Cow i (0-based) is cow number i + 1 and gives i + 1 units of milk.
    milk = [i + 1 for i in cows]
    # Every son gets an equal share of all the milk (no solution when it does not divide evenly).
    milk_per_son = sum(milk) // num_sons

    model = Model("farmer_and_cows")

    # owns[i, s] is 1 when cow i goes to son s.
    owns = model.binary_var_matrix(cows, sons, name="owns")

    # Every cow goes to exactly one son.
    model.add_constraints(model.sum(owns[i, s] for s in sons) == 1 for i in cows)

    for s in sons:
        # Each son gets the number of cows the distribution gives him.
        model.add_constraint(model.sum(owns[i, s] for i in cows) == cows_per_son[s], ctname=f"count_{s}")
        # Each son's cows give the same total quantity of milk.
        model.add_constraint(model.sum(milk[i] * owns[i, s] for i in cows) == milk_per_son, ctname=f"milk_{s}")

    # cow_assignments[i] is the son (0-based) that cow i goes to.
    return model, {"cow_assignments": [model.sum(s * owns[i, s] for s in sons) for i in cows]}


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
