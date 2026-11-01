# arch_friends: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/arch_friends.html
# Run it (after `pip install pychoco numpy`) with:
#   python arch_friends.py

from pychoco.model import Model


def create_model(instance):
    """Harriet bought four pairs of shoes (ecru espadrilles, fuchsia flats, purple
    pumps, suede sandals) at four different stores (Foot Farm, Heels in a
    Handcart, The Shoe Palace, Tootsies). Work out the order in which she bought
    each pair and where she bought each."""
    n_stops = 4  # the number of stops, numbered 1 to 4 in the order she visited them

    model = Model()

    # shoes[k]: the stop at which she bought the k-th pair, in the order ecru espadrilles,
    # fuchsia flats, purple pumps, suede sandals
    shoes = [model.intvar(1, n_stops, name=f"shoe{k}") for k in range(n_stops)]
    ecruespadrilles, fuchsiaflats, purplepumps, suedesandals = shoes
    # store[k]: the stop at which she visited the k-th store, in the order Foot Farm,
    # Heels in a Handcart, The Shoe Palace, Tootsies
    store = [model.intvar(1, n_stops, name=f"store{k}") for k in range(n_stops)]
    footfarm, heelsinahandcart, theshoepalace, tootsies = store

    # Each stop is one pair of shoes, and each stop is one store.
    model.all_different(shoes).post()
    model.all_different(store).post()

    # The fuchsia flats were bought at Heels in a Handcart.
    model.arithm(fuchsiaflats, "=", heelsinahandcart).post()
    # The store visited just after the purple pumps was not Tootsies.
    model.scalar([purplepumps, tootsies], [1, -1], "!=", -1).post()
    # The Foot Farm was the second stop.
    model.arithm(footfarm, "=", 2).post()
    # The suede sandals were bought two stops after The Shoe Palace.
    model.scalar([theshoepalace, suedesandals], [1, -1], "=", -2).post()

    return model, {
        "ecruespadrilles": ecruespadrilles, "fuchsiaflats": fuchsiaflats,
        "purplepumps": purplepumps, "suedesandals": suedesandals,
        "footfarm": footfarm, "heelsinahandcart": heelsinahandcart,
        "theshoepalace": theshoepalace, "tootsies": tootsies,
    }, None


if __name__ == "__main__":
    import numpy as np

    model, outputs, objective = create_model({})
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
