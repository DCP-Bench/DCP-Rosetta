# set_game: a Paramita (Python) model from DCP Rosetta.
# Download the `set_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/set_game.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python set_game.py set_game.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Set card game: from the cards on the table, find three cards that form a set.
    For each of the four features (number, fill, colour, shape), the three cards must
    show it all the same or all different."""
    cards = instance["cards_data"]  # cards[i] holds the number, fill, colour and shape of card i
    n_cards = len(cards)            # the number of cards on the table
    # feature_values[f] lists the values feature f can take
    feature_values = [instance[field] for field in ("numbers", "fills", "colors", "shapes")]
    n_set_cards = 3                 # a set is three cards

    # in_slot[s][i] is true when card i is the s-th card of the set
    in_slot = [[Bool(f"slot_{s}_card_{i}") for i in range(n_cards)] for s in range(n_set_cards)]

    cons = []

    # Each place in the set holds exactly one card.
    for s in range(n_set_cards):
        cons.append(sum(in_slot[s]) == 1)

    # The three cards are different: each card fills at most one place.
    for i in range(n_cards):
        cons.append(sum(in_slot[s][i] for s in range(n_set_cards)) <= 1)

    # For each feature, the three cards are all the same or all different: no value is
    # shown by exactly two of them.
    for f, values in enumerate(feature_values):
        for v in values:
            # the cards that show value v of feature f
            holders = [i for i in range(n_cards) if cards[i][f] == v]
            # how many cards of the set show value v of feature f
            n_shown = sum(in_slot[s][i] for i in holders for s in range(n_set_cards))
            cons.append((n_shown <= 1) | (n_shown >= 3))

    # the table index of the card in each place of the set
    winning_cards = [sum(i * in_slot[s][i] for i in range(n_cards)) for s in range(n_set_cards)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in cons:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"winning_cards": winning_cards}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

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
