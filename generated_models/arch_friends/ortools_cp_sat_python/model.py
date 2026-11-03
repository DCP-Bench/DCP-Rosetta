# arch_friends: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/arch_friends.html
# Run it (after `pip install ortools`) with:
#   python arch_friends.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Harriet bought four pairs of shoes (ecru espadrilles, fuchsia flats, purple
    pumps, suede sandals) at four different stores (Foot Farm, Heels in a
    Handcart, The Shoe Palace, Tootsies). Work out the order in which she bought
    each pair and where she bought each."""
    model = cp_model.CpModel()

    # shoes[k] is the stop at which shoe k was bought
    shoes = [model.new_int_var(1, 4, f"shoe_{k}") for k in range(4)]
    ecruespadrilles, fuchsiaflats, purplepumps, suedesandals = shoes
    # store[k] is the stop at which store k was visited. A shoe bought at the same
    # stop as a store was bought there.
    store = [model.new_int_var(1, 4, f"store_{k}") for k in range(4)]
    footfarm, heelsinahandcart, theshoepalace, tootsies = store

    # Each stop has one shoe and one store.
    model.add_all_different(shoes)
    model.add_all_different(store)
    # Harriet bought the fuchsia flats at Heels in a Handcart.
    model.add(fuchsiaflats == heelsinahandcart)
    # The store visited just after buying the purple pumps was not Tootsies.
    model.add(purplepumps + 1 != tootsies)
    # The Foot Farm was the second stop.
    model.add(footfarm == 2)
    # The suede sandals were bought two stops after The Shoe Palace.
    model.add(theshoepalace + 2 == suedesandals)

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
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
