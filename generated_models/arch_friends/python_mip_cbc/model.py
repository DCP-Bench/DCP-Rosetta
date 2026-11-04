# arch_friends: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/arch_friends.html
# Run it (after `pip install mip numpy`) with:
#   python arch_friends.py

import mip


def add_stop(model, name, n_stops):
    # stop is the stop number, from 1 to n_stops, at which this item is bought or visited
    stop = model.add_var(name, lb=1, ub=n_stops, var_type=mip.INTEGER)
    # at[k] is 1 when this item is at stop k + 1, and 0 when not
    at = [model.add_var(f"{name}_at_{k + 1}", var_type=mip.BINARY) for k in range(n_stops)]
    # Each item is at exactly one stop.
    model.add_constr(mip.xsum(at) == 1)
    # The stop number is the stop at which the item is.
    model.add_constr(stop == mip.xsum((k + 1) * a for k, a in enumerate(at)))
    return stop, at


def create_model(instance):
    """Harriet bought four pairs of shoes (ecru espadrilles, fuchsia flats, purple
    pumps, suede sandals) at four stores (Foot Farm, Heels in a Handcart, The Shoe
    Palace, Tootsies), one pair and one store at each of her four stops. Find the
    stop at which she bought each pair and visited each store."""
    # Harriet makes four stops.
    n_stops = 4

    model = mip.Model(solver_name="CBC")

    # The stop at which each pair of shoes is bought.
    ecruespadrilles, ecru_at = add_stop(model, "ecruespadrilles", n_stops)
    fuchsiaflats, fuchsia_at = add_stop(model, "fuchsiaflats", n_stops)
    purplepumps, purple_at = add_stop(model, "purplepumps", n_stops)
    suedesandals, suede_at = add_stop(model, "suedesandals", n_stops)

    # The stop at which Harriet visits each store.
    footfarm, footfarm_at = add_stop(model, "footfarm", n_stops)
    heelsinahandcart, heels_at = add_stop(model, "heelsinahandcart", n_stops)
    theshoepalace, shoepalace_at = add_stop(model, "theshoepalace", n_stops)
    tootsies, tootsies_at = add_stop(model, "tootsies", n_stops)

    # Harriet buys one pair of shoes at each stop.
    for k in range(n_stops):
        model += mip.xsum(at[k] for at in (ecru_at, fuchsia_at, purple_at, suede_at)) == 1

    # She visits one store at each stop.
    for k in range(n_stops):
        model += mip.xsum(at[k] for at in (footfarm_at, heels_at, shoepalace_at, tootsies_at)) == 1

    # Harriet bought the fuchsia flats at Heels in a Handcart.
    model += fuchsiaflats - heelsinahandcart == 0

    # The store visited just after the purple pumps was not Tootsies.
    for k in range(n_stops - 1):
        model += purple_at[k] + tootsies_at[k + 1] <= 1

    # The Foot Farm was the second stop.
    footfarm.lb = 2
    footfarm.ub = 2

    # The suede sandals were bought two stops after leaving The Shoe Palace.
    model += suedesandals - theshoepalace == 2

    return model, {
        "ecruespadrilles": ecruespadrilles,
        "fuchsiaflats": fuchsiaflats,
        "purplepumps": purplepumps,
        "suedesandals": suedesandals,
        "footfarm": footfarm,
        "heelsinahandcart": heelsinahandcart,
        "theshoepalace": theshoepalace,
        "tootsies": tootsies,
    }


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
