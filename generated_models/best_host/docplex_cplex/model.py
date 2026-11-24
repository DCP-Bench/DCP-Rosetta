# best_host: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/best_host.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python best_host.py

from docplex.mp.model import Model


def create_model(instance):
    """Best host: seat six guests around a round table so that every guest sits only next to the two
    guests they get along with."""
    n = 6  # guests and seats (puzzle constant)
    Andrew, Betty, Cara, Dave, Erica, Frank = range(n)
    # The two guests each guest will sit next to (puzzle constant).
    prefs = [
        [Dave, Frank],   # Andrew
        [Cara, Erica],   # Betty
        [Betty, Frank],  # Cara
        [Andrew, Erica],  # Dave
        [Betty, Dave],   # Erica
        [Andrew, Cara],  # Frank
    ]
    seats = range(n)
    guests = range(n)

    model = Model("best_host")

    # sits[i, g] is 1 when guest g takes seat i
    sits = {(i, g): model.binary_var(name=f"sits_{i}_{g}") for i in seats for g in guests}

    # Every seat has one guest and every guest one seat.
    model.add_constraints(model.sum(sits[i, g] for g in guests) == 1 for i in seats)
    model.add_constraints(model.sum(sits[i, g] for i in seats) == 1 for g in guests)

    # The guests on both sides of a seat (the table is round) are among the two the seated
    # guest will sit next to: a guest g in seat i rules out every other guest h in seats i - 1
    # and i + 1.
    model.add_constraints(sits[i, g] + sits[(i + step) % n, h] <= 1
                          for i in seats for g in guests for h in guests if h not in prefs[g]
                          for step in (-1, 1))

    # x[i] is the guest in seat i, going around the table (Andrew = 0, Betty = 1, ..., Frank = 5).
    return model, {"x": [model.sum(g * sits[i, g] for g in guests) for i in seats]}


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
