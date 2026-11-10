# media_selection: a Paramita (Python) model from DCP Rosetta.
# Download the `media_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/media_selection.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python media_selection.py media_selection.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, add_to_weighted_container, to_cnf


def create_model(instance):
    """Select advertising media so that every target audience is reached by at least one
    selected medium, at the lowest total campaign cost. Reaching an audience more than once
    is fine."""
    audiences = instance["target_audiences"]  # the target audiences
    media = instance["advertising_media"]     # the advertising media
    covers = instance["incidence_matrix"]     # covers[a][m] is 1 if medium m reaches audience a
    costs = instance["media_costs"]           # costs[m]: the cost of medium m

    # is_selected[m] is true when medium m is bought
    select = [Bool(f"select_{m}") for m in range(len(media))]

    # Each audience is reached by at least one selected medium.
    constraints = []
    for a in range(len(audiences)):
        # the selected media that reach audience a
        reaching = [select[m] for m in range(len(media)) if covers[a][m] == 1]
        constraints.append(sum(reaching) >= 1)

    # min_total_cost: the cost of the selected media
    total_cost = sum(costs[m] * select[m] for m in range(len(media)))

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-total_cost, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the total cost, minimised (its negation is
    # what the soft clauses maximise).
    return (formula, pool), {"is_selected": select, "min_total_cost": total_cost}, total_cost


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
