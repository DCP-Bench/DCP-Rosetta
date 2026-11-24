# eighteen_hole_golf: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/eighteen_hole_golf.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python eighteen_hole_golf.py

from docplex.mp.model import Model


def create_model(instance):
    """Eighteen-hole golf: give each of 18 holes a length of 3, 4 or 5 so that the course has a
    total length of 72."""
    num_holes = 18            # holes on the course
    total_length = 72         # the length of the whole course
    shortest, longest = 3, 5  # the shortest and the longest a hole can be

    model = Model("eighteen_hole_golf")

    # Each hole has length 3, 4 or 5.
    holes = [model.integer_var(shortest, longest, name=f"hole_{h}") for h in range(num_holes)]

    # The lengths add up to the course total.
    model.add_constraint(model.sum(holes) == total_length)

    return model, {"holes": holes}


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
