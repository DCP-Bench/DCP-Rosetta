# cell_tower: a Paramita (Python) model from DCP Rosetta.
# Download the `cell_tower.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cell_tower.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python cell_tower.py cell_tower.json

from paramita.containers import WcnfFormula
from paramita.modelling import (
    And, Bool, DimacsVariablePool, Iff, Or, add_to_weighted_container, to_cnf,
)


def create_model(instance):
    """A telecom company chooses at which potential sites to build cell towers, within its budget,
    so that as many inhabitants of the city's regions as possible get signal."""
    cost = instance["cost"]              # cost[i]: the cost of building a tower at site i
    budget = instance["budget"]          # the most the company can spend on towers
    population = instance["population"]  # population[r]: the number of inhabitants of region r
    delta = instance["delta"]            # delta[i][r] is 1 when a tower at site i reaches region r
    n_sites = len(cost)
    n_regions = len(population)

    # build_tower[i] is true when a tower is built at site i
    build_tower = [Bool(f"build_{i}") for i in range(n_sites)]
    # covered[r] is true when region r gets signal
    covered = [Bool(f"covered_{r}") for r in range(n_regions)]

    # The towers built cost no more than the budget.
    constraints = [sum(cost[i] * build_tower[i] for i in range(n_sites)) <= budget]

    # A region gets signal exactly when a built tower reaches it.
    for r in range(n_regions):
        # the sites whose towers reach region r
        reaching = [build_tower[i] for i in range(n_sites) if delta[i][r]]
        if not reaching:
            constraints.append(~covered[r])
        elif len(reaching) == 1:
            constraints.append(Iff(covered[r], reaching[0]))
        else:
            constraints.append(Iff(covered[r], Or(reaching)))

    # The inhabitants of the covered regions, to be maximised.
    covered_population = sum(population[r] * covered[r] for r in range(n_regions))

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # maximise as soft clauses. The pool gives each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(covered_population, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the population covered, maximised (the soft
    # clauses maximise it).
    return (formula, pool), {"build_tower": build_tower, "total_population_covered": covered_population}, covered_population


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
