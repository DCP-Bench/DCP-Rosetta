# allergy: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/allergy.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python allergy.py

from docplex.mp.model import Model


def create_model(instance):
    """Allergy logic puzzle: four friends (Debra, Janet, Hugh, Rick) each have a different surname
    (Baxter, Lemon, Malone, Fleet) and a different allergy (eggs, mold, nuts, ragweed); match them
    using the given clues."""
    n = 4  # four friends, four allergies, four surnames (puzzle constant)
    Debra, Janet, Hugh, Rick = range(n)  # the friend numbers of the output: Debra = 0, Janet = 1, Hugh = 2, Rick = 3
    friends = range(n)
    foods = ["eggs", "mold", "nuts", "ragweed"]
    surnames = ["baxter", "lemon", "malone", "fleet"]

    model = Model("allergy")

    # has[x, f] is 1 when allergy or surname x belongs to friend f
    has = {(x, f): model.binary_var(name=f"{x}_{f}") for x in foods + surnames for f in friends}

    # Each friend has a different allergy and a different surname.
    for group in (foods, surnames):
        model.add_constraints(model.sum(has[x, f] for f in friends) == 1 for x in group)
        model.add_constraints(model.sum(has[x, f] for x in group) == 1 for f in friends)

    # Rick is not allergic to mold.
    model.add_constraint(has["mold", Rick] == 0)
    # Baxter is allergic to eggs.
    model.add_constraints(has["eggs", f] == has["baxter", f] for f in friends)
    # Hugh is neither surnamed Lemon nor Fleet.
    model.add_constraint(has["lemon", Hugh] == 0)
    model.add_constraint(has["fleet", Hugh] == 0)
    # Debra is allergic to ragweed.
    model.add_constraint(has["ragweed", Debra] == 1)
    # Janet (who isn't Lemon) is neither allergic to eggs nor to mold.
    model.add_constraint(has["lemon", Janet] == 0)
    model.add_constraint(has["eggs", Janet] == 0)
    model.add_constraint(has["mold", Janet] == 0)

    # For each allergy and each surname, the number of the friend who has it.
    return model, {x: model.sum(f * has[x, f] for f in friends) for x in foods + surnames}


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
