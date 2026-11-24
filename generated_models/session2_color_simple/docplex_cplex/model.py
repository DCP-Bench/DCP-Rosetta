# session2_color_simple: a CPLEX (Python) model from DCP Rosetta.
# Download the `session2_color_simple.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_color_simple.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python session2_color_simple.py session2_color_simple.json

from docplex.mp.model import Model


def create_model(instance):
    """Map colouring: colour Belgium, Denmark, France, Germany, the Netherlands and Luxembourg so
    that neighbouring countries differ, using as few colours as possible."""
    graph = instance["graph"]  # pairs (i, j) of neighbouring countries, numbered from 1
    # Belgium, Denmark, France, Germany, the Netherlands and Luxembourg
    num_nodes = 6
    countries = range(num_nodes)
    # Colours 1..6: no colouring needs more colours than there are countries, so this cuts off no optimum.
    palette = range(1, num_nodes + 1)

    model = Model("color_simple")

    # paint[i, c] is 1 when country i gets colour c
    paint = {(i, c): model.binary_var(name=f"country_{i + 1}_colour_{c}") for i in countries
             for c in palette}

    # Each country gets exactly one colour.
    model.add_constraints(model.sum(paint[i, c] for c in palette) == 1 for i in countries)

    # colors[i] is the colour number of country i
    colors = [model.sum(c * paint[i, c] for c in palette) for i in countries]

    # Two neighbouring countries cannot have the same colour.
    model.add_constraints(paint[i - 1, c] + paint[j - 1, c] <= 1 for i, j in graph for c in palette)

    # Minimise the number of colours used. This is the largest colour number: at an optimum no
    # colour below it is skipped, so it equals the number of different colours.
    used = model.integer_var(1, num_nodes, name="max_colour")
    model.add_constraints(used >= colors[i] for i in countries)
    model.minimize(used)

    return model, {"colors": colors}


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
