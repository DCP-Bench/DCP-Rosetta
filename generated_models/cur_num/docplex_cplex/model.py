# cur_num: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cur_num.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python cur_num.py

from docplex.mp.model import Model


def create_model(instance):
    """Curious numbers (Dudeney 114): 48 plus 1 is a square, and half of 48 plus 1 is a square.
    Find another number between 1 and 10000 with this property."""
    top = 10000  # the number looked for is between 1 and top
    known = 48   # the example in the statement; the number looked for is another one

    model = Model("cur_num")

    # peculiar is the number looked for, and half is its half
    peculiar = model.integer_var(1, top, name="peculiar")
    half = model.integer_var(1, top, name="half")

    # A square up to top has a root up to the square root of top. root_is[r] is 1 when the square's root is
    # r; a square is read as sum of r * r over the chosen root, since CPLEX refuses b * b
    # for a variable b.
    roots = [r for r in range(1, top + 1) if r * r <= top]

    def square(name):
        root_is = [model.binary_var(name=f"{name}_root_{r}") for r in roots]
        model.add_constraint(model.sum(root_is) == 1)
        return model.sum(r * r * b for r, b in zip(roots, root_is))

    # 48 is already known.
    model.add(peculiar != known)
    # Adding 1 to the number gives a square.
    model.add_constraint(peculiar + 1 == square("plus_one"))
    # The number's half, plus 1, is also a square.
    model.add_constraint(peculiar == 2 * half)
    model.add_constraint(half + 1 == square("half_plus_one"))

    return model, {"peculiar": peculiar}


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
