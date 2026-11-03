# arch_friends: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/arch_friends.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python arch_friends.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Harriet bought four pairs of shoes at four stores, one pair and one store per
    stop. Find the order of the stops, and which shoe and which store goes with each."""
    stops = [1, 2, 3, 4]  # the stops, numbered in the order Harriet made them
    shoes = ["ecruespadrilles", "fuchsiaflats", "purplepumps", "suedesandals"]  # the four pairs of shoes
    stores = ["footfarm", "heelsinahandcart", "theshoepalace", "tootsies"]  # the four stores

    # shoe_at[s][p] is true when the pair of shoe s is bought at stop p
    shoe_at = {s: {p: Bool(f"shoe_{s}_{p}") for p in stops} for s in shoes}
    # store_at[t][p] is true when Harriet visits store t at stop p
    store_at = {t: {p: Bool(f"store_{t}_{p}") for p in stops} for t in stores}

    # The stop number of a shoe or a store: the stop whose flag is true.
    def stop_of(flags):
        return sum(p * flags[p] for p in stops)

    constraints = []  # the rules the stops must satisfy
    # Each shoe is bought at exactly one stop, and each stop has one shoe.
    for s in shoes:
        constraints.append(sum(shoe_at[s].values()) == 1)
    for p in stops:
        constraints.append(sum(shoe_at[s][p] for s in shoes) == 1)
    # Each store is visited at exactly one stop, and each stop has one store.
    for t in stores:
        constraints.append(sum(store_at[t].values()) == 1)
    for p in stops:
        constraints.append(sum(store_at[t][p] for t in stores) == 1)
    # Harriet bought the fuchsia flats at Heels in a Handcart, so both are at the same stop.
    constraints.append(stop_of(shoe_at["fuchsiaflats"]) == stop_of(store_at["heelsinahandcart"]))
    # The store visited just after the purple pumps was not Tootsies.
    for k in stops[:-1]:
        constraints.append(~(shoe_at["purplepumps"][k] & store_at["tootsies"][k + 1]))
    # The Foot Farm was the second stop.
    constraints.append(store_at["footfarm"][2])
    # The suede sandals were bought two stops after The Shoe Palace.
    constraints.append(stop_of(store_at["theshoepalace"]) + 2 == stop_of(shoe_at["suedesandals"]))

    # The stop number of each shoe and of each store.
    outputs = {**{s: stop_of(shoe_at[s]) for s in shoes}, **{t: stop_of(store_at[t]) for t in stores}}

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), outputs


if __name__ == "__main__":
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    (formula, pool), outputs = create_model({})

    solver = SatSolver.from_name("Cadical300")
    # copy the formula into the solver
    solver.add_clauses(formula.clauses())

    if solver.solve():
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
