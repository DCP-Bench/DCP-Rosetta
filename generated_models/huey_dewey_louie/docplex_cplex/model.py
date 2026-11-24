# huey_dewey_louie: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/huey_dewey_louie.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python huey_dewey_louie.py

from docplex.mp.model import Model


def create_model(instance):
    """Huey, Dewey and Louie: from three truthful statements, decide which of them are guilty."""
    model = Model("huey_dewey_louie")

    # Each variable is 1 when that nephew is guilty, and 0 when not.
    huey = model.binary_var(name="huey")
    dewey = model.binary_var(name="dewey")
    louie = model.binary_var(name="louie")

    # Huey: Dewey and Louie share equally; if one is guilty, so is the other.
    model.add_constraint(dewey == louie)
    # Dewey: if Huey is guilty, then so am I.
    model.add_constraint(huey <= dewey)
    # Louie: Dewey and I are not both guilty.
    model.add_constraint(dewey + louie <= 1)

    return model, {"huey": huey, "dewey": dewey, "louie": louie}


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
