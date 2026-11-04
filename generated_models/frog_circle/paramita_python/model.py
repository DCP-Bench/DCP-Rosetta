# frog_circle: a Paramita (Python) model from DCP Rosetta.
# Download the `frog_circle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/frog_circle.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python frog_circle.py frog_circle.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, add_to_container, to_cnf


def create_model(instance):
    """Cards numbered 1 to n_cards lie on a circle. A frog starts on card 1 and, from card k,
    jumps k places clockwise. Arrange the cards so that the frog lands on every card."""
    n_cards = instance["n"]  # the number of cards, numbered 1 to n_cards
    cards = range(1, n_cards + 1)
    positions = range(n_cards)  # the places on the circle, clockwise from place 0

    # card_at[p][v] is true when card v is at position p of the circle.
    card_at = [{v: Bool(f"x_{p}_{v}") for v in cards} for p in positions]

    # frog_at[i][p] is true when the frog stands on position p after i jumps.
    frog_at = [[Bool(f"y_{i}_{p}") for p in positions] for i in range(n_cards)]

    # Each position holds exactly one card.
    subject_to = [sum(card_at[p].values()) == 1 for p in positions]

    # Each card is at exactly one position.
    subject_to += [sum(card_at[p][v] for p in positions) == 1 for v in cards]

    # The frog starts on card 1, at position 0.
    subject_to += [card_at[0][1], frog_at[0][0]]

    # The frog stands on exactly one position after each number of jumps.
    subject_to += [sum(frog_at[i]) == 1 for i in range(n_cards)]

    # The frog stands on each position exactly once over its n_cards stops, so it lands on every card.
    subject_to += [sum(frog_at[i][p] for i in range(n_cards)) == 1 for p in positions]

    # From card v at position p, the frog jumps v places clockwise to position (p + v) mod n_cards.
    for i in range(n_cards - 1):
        for p in positions:
            for v in cards:
                q = (p + v) % n_cards
                subject_to.append(If(frog_at[i][p] & card_at[p][v], frog_at[i + 1][q]))

    # x[p] is the number of the card at position p.
    x = [sum(v * card_at[p][v] for v in cards) for p in positions]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in subject_to:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"x": x}


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
