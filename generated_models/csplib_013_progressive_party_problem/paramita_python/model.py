# csplib_013_progressive_party_problem: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_013_progressive_party_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_013_progressive_party_problem.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python csplib_013_progressive_party_problem.py csplib_013_progressive_party_problem.json

from paramita.containers import WcnfFormula
from paramita.modelling import (
    And, Bool, DimacsVariablePool, If, Iff, add_to_weighted_container, to_cnf,
)


def create_model(instance):
    """Timetable a party at a yacht club: some boats are hosts, and the crews of the
    other boats visit host boats in successive half-hour periods. No boat may hold more
    people than its capacity, a guest crew never revisits a host, and two guest crews
    meet at most once. Use as few host boats as possible."""
    n_boats = instance["n_boats"]      # the number of boats
    n_periods = instance["n_periods"]  # the number of half-hour periods
    capacity = instance["capacity"]    # capacity[b]: the most people boat b can hold
    crew_size = instance["crew_size"]  # crew_size[b]: the number of people in the crew of boat b

    boats = range(n_boats)
    periods = range(n_periods)

    # is_host[b] is true when boat b is a host boat
    is_host = [Bool(f"is_host_{b}") for b in boats]
    # at[p][b][t] is true when in period p the crew of boat b is aboard boat t
    at = [[[Bool(f"at_{p}_{b}_{t}") for t in boats] for b in boats] for p in periods]

    constraints = []

    # Each crew is aboard exactly one boat in each period.
    for p in periods:
        for b in boats:
            constraints.append(sum(at[p][b]) == 1)

    # A host crew stays aboard its own boat, and a guest crew does not.
    for p in periods:
        for b in boats:
            constraints.append(Iff(at[p][b][b], is_host[b]))

    # A guest crew visits host boats only.
    for p in periods:
        for b in boats:
            for t in boats:
                if t != b:
                    constraints.append(If(at[p][b][t], is_host[t]))

    # The people aboard a host boat, its own crew and the guest crews, stay within its capacity.
    for p in periods:
        for h in boats:
            aboard = sum(crew_size[g] * at[p][g][h] for g in boats if g != h) + crew_size[h] * is_host[h]
            constraints.append(aboard <= capacity[h])

    # A guest crew does not revisit a host.
    for g in boats:
        for h in boats:
            if h != g:
                constraints.append(sum(at[p][g][h] for p in periods) <= 1)

    # Two guest crews meet at most once.
    for g in boats:
        for g2 in boats:
            if g2 <= g:
                continue
            # met[p] is true when crews g and g2 are aboard the same boat in period p
            met = [Bool(f"met_{p}_{g}_{g2}") for p in periods]
            for p in periods:
                for t in boats:
                    constraints.append(If(And(at[p][g][t], at[p][g2][t]), met[p]))
            constraints.append(sum(met) <= 1)

    # visits[p][b]: the boat the crew of boat b is aboard in period p
    visits = [[sum(t * at[p][b][t] for t in boats) for b in boats] for p in periods]

    # Use as few host boats as possible.
    n_hosts = sum(is_host)

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-n_hosts, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the number of host boats, minimised (its
    # negation is what the soft clauses maximise).
    return (formula, pool), {"is_host": is_host, "visits": visits}, n_hosts


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
