# arch_friends: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/arch_friends.html
# Run it (after `pip install pulp numpy`) with:
#   python arch_friends.py

import pulp


def create_model(instance):
    """Harriet bought four pairs of shoes (ecru espadrilles, fuchsia flats, purple
    pumps, suede sandals) at four different stores (Foot Farm, Heels in a
    Handcart, The Shoe Palace, Tootsies). Work out the order in which she bought
    each pair and where she bought each."""
    stops = range(1, 5)  # Harriet's four stops, numbered 1 to 4
    shoe_names = ["ecruespadrilles", "fuchsiaflats", "purplepumps", "suedesandals"]
    store_names = ["footfarm", "heelsinahandcart", "theshoepalace", "tootsies"]

    problem = pulp.LpProblem("arch_friends", pulp.LpMinimize)

    # at[name][s] is 1 when the shoe or store called name belongs to stop s, and 0 when not
    at = {name: {s: pulp.LpVariable(f"at_{name}_{s}", cat="Binary") for s in stops}
          for name in shoe_names + store_names}

    # Each shoe and each store has exactly one stop, and each stop has one shoe and one store.
    for group in (shoe_names, store_names):
        for name in group:
            problem += pulp.lpSum(at[name].values()) == 1
        for s in stops:
            problem += pulp.lpSum(at[name][s] for name in group) == 1

    # stop_of[name] is the stop at which the shoe was bought or the store was visited.
    stop_of = {name: pulp.lpSum(s * at[name][s] for s in stops) for name in at}

    # Harriet bought the fuchsia flats at Heels in a Handcart.
    problem += stop_of["fuchsiaflats"] == stop_of["heelsinahandcart"]

    # The store she visited just after buying the purple pumps was not Tootsies.
    for s in stops[:-1]:
        problem += at["purplepumps"][s] + at["tootsies"][s + 1] <= 1

    # The Foot Farm was Harriet's second stop.
    problem += at["footfarm"][2] == 1

    # Two stops after leaving The Shoe Palace, Harriet bought her suede sandals.
    problem += stop_of["theshoepalace"] + 2 == stop_of["suedesandals"]

    return problem, stop_of


if __name__ == "__main__":
    import numpy as np

    problem, outputs = create_model({})
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
