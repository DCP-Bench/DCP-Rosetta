# dinner: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dinner.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python dinner.py

from docplex.mp.model import Model


def create_model(instance):
    """Dinner: 20 people go to dinner for $20 in total; grandparents cost $3, parents $2 and
    children $0.50. How many of each go?"""
    n_people = 20  # people at dinner, in total
    budget = 20    # dollars the dinner costs, in total

    model = Model("dinner")

    # 1-6 grandparents, 1-10 parents and 1-40 children.
    grandparents = model.integer_var(1, 6, name="grandparents")
    parents = model.integer_var(1, 10, name="parents")
    children = model.integer_var(1, 40, name="children")

    # The dinner costs $20: $3 a grandparent, $2 a parent, $0.50 a child, counted in half
    # dollars so every coefficient is an integer.
    model.add_constraint(6 * grandparents + 4 * parents + children == 2 * budget)
    # There are 20 people in total.
    model.add_constraint(grandparents + parents + children == n_people)

    return model, {"grandparents": grandparents, "parents": parents, "children": children}


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
