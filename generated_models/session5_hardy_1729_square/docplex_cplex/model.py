# session5_hardy_1729_square: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_hardy_1729_square.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python session5_hardy_1729_square.py

from docplex.mp.model import Model


def create_model(instance):
    """Hardy 1729, squares version: four different numbers a, b, c, d in 1..100 with
    a^2 + b^2 = c^2 + d^2."""
    range_min, range_max = 1, 100  # the numbers lie between 1 and 100
    names = "abcd"                 # the four numbers a, b, c and d
    values = range(range_min, range_max + 1)

    model = Model("hardy_1729_square")

    # is_value[x, v] is 1 when number x is v. CPLEX refuses x * x == ..., so each number is
    # chosen from its values and its square is read as sum of v * v over the choice.
    is_value = {(x, v): model.binary_var(name=f"{x}_is_{v}") for x in names for v in values}
    model.add_constraints(model.sum(is_value[x, v] for v in values) == 1 for x in names)

    # The four numbers are all different: no value is taken twice.
    model.add_constraints(model.sum(is_value[x, v] for x in names) <= 1 for v in values)

    def square(x):  # the square of number x, as a linear expression
        return model.sum(v * v * is_value[x, v] for v in values)

    # a^2 + b^2 = c^2 + d^2.
    model.add_constraint(square("a") + square("b") == square("c") + square("d"))

    # a, b, c and d are read back as the value chosen for each number.
    return model, {x: model.sum(v * is_value[x, v] for v in values) for x in names}


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
