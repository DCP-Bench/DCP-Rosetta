# arch_friends: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/arch_friends.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python arch_friends.py

from pyscipopt import Model, quicksum


def create_model(instance):
    """Harriet bought four pairs of shoes (ecru espadrilles, fuchsia flats,
    purple pumps, suede sandals), one pair at each of four stops, at four stores
    (Foot Farm, Heels in a Handcart, The Shoe Palace, Tootsies). Find which shoe
    and which store belong to each stop, from the four clues. The stops are
    numbered 1 to 4 in the order Harriet visited them.

    The instance is empty ({} in the run block): every fact comes from the
    problem statement, so the instance argument is not read."""
    # The four shoes and the four stores, under the names the outputs use.
    shoes = ["ecruespadrilles", "fuchsiaflats", "purplepumps", "suedesandals"]
    stores = ["footfarm", "heelsinahandcart", "theshoepalace", "tootsies"]
    # The stops are the numbers 1 to 4 in the order Harriet visited them.
    stops = range(1, 5)

    model = Model("arch_friends")

    # SCIP has no all-different constraint, so each stop is chosen with one-hot binaries
    # (one per shoe and stop, one per store and stop). 'Each stop used once' then states
    # that all shoes, and all stores, are at different stops. The integer stop numbers
    # below are the outputs, and clues 1, 3 and 4 are written on them directly.

    # bought[shoe, stop] is 1 when Harriet bought that shoe at that stop, and 0 when not
    bought = {(s, p): model.addVar(f"bought_{s}_{p}", vtype="B") for s in shoes for p in stops}
    # visited[store, stop] is 1 when Harriet shopped at that store at that stop, and 0 when not
    visited = {(t, p): model.addVar(f"visited_{t}_{p}", vtype="B") for t in stores for p in stops}

    # shoe_stop[shoe] is the stop at which the shoe was bought, an integer from 1 to 4.
    # The bounds 1 to 4 come from the statement: "values are integers from 1 to 4".
    shoe_stop = {s: model.addVar(f"shoe_stop_{s}", vtype="I", lb=1, ub=4) for s in shoes}
    # store_stop[store] is the stop at which Harriet shopped there, an integer from 1 to 4.
    store_stop = {t: model.addVar(f"store_stop_{t}", vtype="I", lb=1, ub=4) for t in stores}

    # Each shoe is bought at exactly one stop, and its stop number is that stop.
    for s in shoes:
        model.addCons(quicksum(bought[s, p] for p in stops) == 1)
        model.addCons(shoe_stop[s] == quicksum(p * bought[s, p] for p in stops))

    # Each store is visited at exactly one stop, and its stop number is that stop.
    for t in stores:
        model.addCons(quicksum(visited[t, p] for p in stops) == 1)
        model.addCons(store_stop[t] == quicksum(p * visited[t, p] for p in stops))

    # All different: each stop has exactly one shoe bought there and exactly one store
    # visited there (four pairs, four stores, four stops).
    for p in stops:
        model.addCons(quicksum(bought[s, p] for s in shoes) == 1)
        model.addCons(quicksum(visited[t, p] for t in stores) == 1)

    # Clue 1: Harriet bought fuchsia flats at Heels in a Handcart, so both are at the same stop.
    model.addCons(shoe_stop["fuchsiaflats"] == store_stop["heelsinahandcart"])

    # Clue 2: the store visited just after buying the purple pumps was not Tootsies.
    # SCIP's addCons cannot state '!=', so the clue is written on the one-hot binaries:
    # purple pumps at stop p and Tootsies at stop p + 1 cannot both hold. The last stop
    # has no stop after it, so no restriction is written there.
    for p in range(1, 4):
        model.addCons(bought["purplepumps", p] + visited["tootsies", p + 1] <= 1)

    # Clue 3: The Foot Farm was Harriet's second stop.
    model.addCons(store_stop["footfarm"] == 2)

    # Clue 4: two stops after leaving The Shoe Palace (the statement's "The Shoe Place"),
    # Harriet bought the suede sandals. So the sandals' stop is the palace's stop plus 2.
    model.addCons(shoe_stop["suedesandals"] == store_stop["theshoepalace"] + 2)

    # There is no objective: the task asks for values that satisfy the clues.
    outputs = {s: shoe_stop[s] for s in shoes}
    outputs.update({t: store_stop[t] for t in stores})
    return model, outputs


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
