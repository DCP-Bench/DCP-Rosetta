# session1_five_floors: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_five_floors.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python session1_five_floors.py

from docplex.mp.model import Model


def create_model(instance):
    """Baker, Cooper, Fletcher, Miller and Smith live on different floors of the first five floors
    of an apartment house; find the floor of each from the clues."""
    people = ["B", "C", "F", "M", "S"]  # Baker, Cooper, Fletcher, Miller, Smith
    floors = range(1, 6)  # the first five floors

    model = Model("five_floors")

    # lives[p, f] is 1 when person p lives on floor f
    lives = {(p, f): model.binary_var(name=f"{p}_on_{f}") for p in people for f in floors}

    # Everyone lives on exactly one floor.
    model.add_constraints(model.sum(lives[p, f] for f in floors) == 1 for p in people)

    # They all live on different floors.
    model.add_constraints(model.sum(lives[p, f] for p in people) == 1 for f in floors)

    # floor[p] is the floor on which person p lives
    floor = {p: model.sum(f * lives[p, f] for f in floors) for p in people}

    # Baker does not live on the fifth floor.
    model.add_constraint(lives["B", 5] == 0)
    # Cooper does not live on the first floor.
    model.add_constraint(lives["C", 1] == 0)
    # Fletcher lives on neither the fifth nor the first floor.
    model.add_constraint(lives["F", 5] + lives["F", 1] == 0)
    # Miller lives on a higher floor than Cooper.
    model.add_constraint(floor["M"] >= floor["C"] + 1)

    def not_adjacent(p, q):
        # p and q do not live on neighbouring floors f and f + 1, in either order.
        for f in floors:
            if f + 1 in floors:
                model.add_constraint(lives[p, f] + lives[q, f + 1] <= 1)
                model.add_constraint(lives[p, f + 1] + lives[q, f] <= 1)

    # Smith does not live on a floor adjacent to Fletcher's.
    not_adjacent("S", "F")
    # Fletcher does not live on a floor adjacent to Cooper's.
    not_adjacent("F", "C")

    return model, dict(floor)


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
