# netasgn: a Paramita (Python) model from DCP Rosetta.
# Download the `netasgn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/netasgn.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python netasgn.py netasgn.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, If, add_to_weighted_container, to_cnf


def create_model(instance):
    """Assign hours from people to projects at the lowest total cost, so that each person
    works exactly their available hours, each project gets exactly the hours it requires,
    and no person works more than the limit on a project."""
    supply = instance["supply"]  # supply[i]: the hours person i has available
    demand = instance["demand"]  # demand[j]: the hours project j requires
    cost = instance["cost"]      # cost[i][j]: the cost of one hour of person i on project j
    limit = instance["limit"]    # limit[i][j]: the most hours person i can work on project j
    n_people = len(supply)       # number of people
    n_projects = len(demand)     # number of projects

    # at_least[i][j][k] is true when person i works at least k + 1 hours on project j,
    # for k = 0 .. limit[i][j] - 1. The hours worked are the number of true statements.
    at_least = [[[Bool(f"at_least_{i}_{j}_{k + 1}") for k in range(limit[i][j])]
                 for j in range(n_projects)]
                for i in range(n_people)]

    # Being at least k + 1 hours implies being at least k hours.
    cons = []
    for i in range(n_people):
        for j in range(n_projects):
            for k in range(limit[i][j] - 1):
                cons.append(If(at_least[i][j][k + 1], at_least[i][j][k]))

    def total(terms):
        # An empty sum is the number 0.
        return sum(terms) if terms else 0

    def equal_to(terms, k):
        # With no statements to count, the total is 0 and cannot be k > 0.
        if terms:
            return sum(terms) == k
        if k == 0:
            return None
        impossible = Bool("no_hours_available")
        return impossible & ~impossible

    # Each person works exactly their available hours.
    for i in range(n_people):
        terms = [b for j in range(n_projects) for b in at_least[i][j]]
        c = equal_to(terms, supply[i])
        if c is not None:
            cons.append(c)

    # Each project gets exactly the hours it requires.
    for j in range(n_projects):
        terms = [b for i in range(n_people) for b in at_least[i][j]]
        c = equal_to(terms, demand[j])
        if c is not None:
            cons.append(c)

    # assign[i][j] is the number of hours person i works on project j.
    assign = [[total(at_least[i][j]) for j in range(n_projects)] for i in range(n_people)]

    # The total cost is the cost of every hour worked.
    total_cost = total([cost[i][j] * b
                        for i in range(n_people)
                        for j in range(n_projects)
                        for b in at_least[i][j]])

    # Minimise the total cost.

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-total_cost, And(cons), to_cnf, formula, pool)

    # The objective in the problem's terms: the total cost, minimised (its negation is
    # what the soft clauses maximise).
    return (formula, pool), {"assign": assign, "total_cost": total_cost}, total_cost


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
