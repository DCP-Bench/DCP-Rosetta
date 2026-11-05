# mario: a Paramita (Python) model from DCP Rosetta.
# Download the `mario.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/mario.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python mario.py mario.json

from paramita.containers import WcnfFormula
from paramita.modelling import (
    And, Bool, DimacsVariablePool, If, Iff, Or, add_to_weighted_container, to_cnf,
)


def create_model(instance):
    """Mario drives from his house to Luigi's house, visiting houses on the way to collect
    their gold, and the fuel used on the drive stays within the limit. He collects as much
    gold as possible."""
    n_houses = instance["nHouses"]        # the number of houses, numbered 0 to n_houses - 1
    mario = instance["marioHouse"]        # the house where Mario starts
    luigi = instance["luigiHouse"]        # the house where Mario ends
    fuel = instance["arc_fuel"]           # fuel[i][j]: the fuel to drive from house i to house j
    gold = instance["goldInHouse"]        # gold[i]: the gold in house i
    fuel_limit = instance["fuelLimit"]    # the most fuel the drive may use
    houses = range(n_houses)

    # arc[i][j] is true when Mario drives straight from house i to house j.
    # Luigi's house is left only for Mario's house, and Mario's house is entered only from Luigi's house.
    arc = [[None] * n_houses for _ in houses]
    for i in houses:
        for j in houses:
            if i == j:
                continue
            if (i == luigi) != (j == mario):
                continue
            if fuel[i][j] > fuel_limit:
                continue
            arc[i][j] = Bool(f"arc_{i}_{j}")

    # The drives that leave house i.
    def out_arcs(i):
        return [arc[i][j] for j in houses if arc[i][j] is not None]

    # The drives that enter house j.
    def in_arcs(j):
        return [arc[i][j] for i in houses if arc[i][j] is not None]

    # visited[i] is true when house i is on the route.
    visited = [Bool(f"visited_{i}") for i in houses]

    # pos[(i, k)] is true when house i comes at least k stops after Mario's house.
    pos = {(i, k): Bool(f"pos_{i}_ge_{k}") for i in houses for k in range(1, n_houses)}

    cons = []  # the rules of the route

    # A house is on the route exactly when a drive leaves it.
    cons += [Iff(visited[i], Or(out_arcs(i))) for i in houses]

    # A house at least k + 1 stops after Mario's house is also at least k stops after it.
    for i in houses:
        cons += [If(pos[(i, k + 1)], pos[(i, k)]) for k in range(1, n_houses - 1)]
    # Mario's house is stop 0.
    cons += [~pos[(mario, k)] for k in range(1, n_houses)]

    # Mario's house is left once, and Luigi's house is left once, for Mario's house.
    cons.append(sum(out_arcs(mario)) == 1)
    cons.append(sum(out_arcs(luigi)) == 1)
    # Luigi's house is entered once, and Mario's house is entered once, from Luigi's house.
    cons.append(sum(in_arcs(luigi)) == 1)
    cons.append(sum(in_arcs(mario)) == 1)

    # Every other house is entered as often as it is left, and at most once each way.
    for i in houses:
        if i in (mario, luigi):
            continue
        cons.append(sum(out_arcs(i)) == sum(in_arcs(i)))
        cons.append(sum(out_arcs(i)) <= 1)
        cons.append(sum(in_arcs(i)) <= 1)

    # A drive from house i into a house j other than Mario's raises the stop count by at least one,
    # which rules out loops that do not pass Mario's house.
    for i in houses:
        for j in houses:
            drive = arc[i][j]
            if drive is None or j == mario:
                continue
            cons.append(If(drive, pos[(j, 1)]))
            if i != mario:
                for k in range(1, n_houses - 1):
                    cons.append(If(drive, If(pos[(i, k)], pos[(j, k + 1)])))
                cons.append(If(drive, ~pos[(i, n_houses - 1)]))

    # The fuel of the drives made stays within the fuel limit.
    cons.append(sum(fuel[i][j] * arc[i][j] for i in houses for j in houses if arc[i][j] is not None) <= fuel_limit)

    # s[i] is the house that follows house i on the route, or i itself when house i is not on the route.
    s = [i + sum((j - i) * arc[i][j] for j in houses if arc[i][j] is not None) for i in houses]

    # The gold collected: the gold of each house on the route.
    total_gold = sum(gold[i] * visited[i] for i in houses)

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # maximise as soft clauses. The pool gives each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(total_gold, And(cons), to_cnf, formula, pool)

    # The objective in the problem's terms: the gold collected, maximised (the soft
    # clauses maximise it).
    return (formula, pool), {"s": s}, total_gold


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
