# session2_color_simple: a Paramita (Python) model from DCP Rosetta.
# Download the `session2_color_simple.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_color_simple.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python session2_color_simple.py session2_color_simple.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, Or, add_to_weighted_container, to_cnf


def create_model(instance):
    """Give each country a colour, an integer starting from 1, so that two
    neighbouring countries never share a colour, using as few colours as possible."""
    graph = instance["graph"]                       # pairs [a, b] of neighbouring countries, numbered from 1
    n_countries = max(max(pair) for pair in graph)  # the countries are numbered 1 to n_countries
    n_colours = n_countries                         # every country can have its own colour

    # gets[i][c] is true when country i+1 gets colour c+1
    gets = [[Bool(f"gets_{i}_{c}") for c in range(n_colours)] for i in range(n_countries)]

    subject_to = []  # the rules the colouring must satisfy

    # Each country gets exactly one colour.
    for i in range(n_countries):
        subject_to.append(sum(gets[i]) == 1)

    # Neighbouring countries get different colours.
    for a, b in graph:
        for c in range(n_colours):
            subject_to.append(~(gets[a - 1][c] & gets[b - 1][c]))

    # colors[i] is the colour of country i+1
    colors = [sum((c + 1) * gets[i][c] for c in range(n_colours)) for i in range(n_countries)]

    # used[c] is true when some country gets colour c+1
    used = [Or([gets[i][c] for i in range(n_countries)]) for c in range(n_colours)]

    # Colours are used from 1 up without a gap, so the number of colours used is the highest
    # colour, which is what is minimised.
    for c in range(1, n_colours):
        subject_to.append(~used[c] | used[c - 1])
    n_colours_used = sum(used)

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-n_colours_used, And(subject_to), to_cnf, formula, pool)

    # The objective in the problem's terms: the number of colours used, minimised (its
    # negation is what the soft clauses maximise).
    return (formula, pool), {"colors": colors}, n_colours_used


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs, objective = create_model(instances[index])

    solver = MaxSatSolver.from_name("EvalMaxSAT2022")
    # copy the formula into the solver: the hard clauses, then each soft clause with its weight
    solver.add_clauses(formula.hard_clauses())
    for weight, clause in formula.soft_clauses():
        solver.add_clause(clause, weight)

    if solver.solve() == MAXSAT_ANSWER.OPTIMAL:
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
        print("objective =", evaluate(objective, truth))
    else:
        print("No solution")
