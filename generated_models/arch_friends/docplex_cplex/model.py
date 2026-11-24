# arch_friends: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/arch_friends.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python arch_friends.py

from docplex.mp.model import Model


def create_model(instance):
    """Arch friends logic puzzle: Harriet bought four different pairs of shoes (ecru espadrilles,
    fuchsia flats, purple pumps, suede sandals) at four different stores (Foot Farm, Heels in a
    Handcart, The Shoe Palace, Tootsies), one per stop; find the stop (1..4) of each shoe and each
    store from the clues."""
    n = 4  # four stops (puzzle constant)
    stops = range(1, n + 1)
    shoes = ["ecruespadrilles", "fuchsiaflats", "purplepumps", "suedesandals"]
    stores = ["footfarm", "heelsinahandcart", "theshoepalace", "tootsies"]

    model = Model("arch_friends")

    # at[x, s] is 1 when shoe or store x belongs to stop s
    at = {(x, s): model.binary_var(name=f"{x}_{s}") for x in shoes + stores for s in stops}

    # Every shoe is bought at a different stop, and every store is visited at a different stop.
    for group in (shoes, stores):
        model.add_constraints(model.sum(at[x, s] for s in stops) == 1 for x in group)
        model.add_constraints(model.sum(at[x, s] for x in group) == 1 for s in stops)

    # 1. Harriet bought fuchsia flats at Heels in a Handcart.
    model.add_constraints(at["fuchsiaflats", s] == at["heelsinahandcart", s] for s in stops)

    # 2. The store she visited just after buying her purple pumps was not Tootsies.
    model.add_constraints(at["purplepumps", s] + at["tootsies", s + 1] <= 1 for s in stops if s + 1 in stops)

    # 3. The Foot Farm was Harriet's second stop.
    model.add_constraint(at["footfarm", 2] == 1)

    # 4. Two stops after leaving The Shoe Palace, Harriet bought her suede sandals.
    # (no stop lies two before stops 1 and 2, so the sandals are not bought there)
    model.add_constraints(at["suedesandals", s] == (at["theshoepalace", s - 2] if s - 2 in stops else 0)
                          for s in stops)

    # For each shoe and each store, the number of its stop (1 to 4).
    return model, {x: model.sum(s * at[x, s] for s in stops) for x in shoes + stores}


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
