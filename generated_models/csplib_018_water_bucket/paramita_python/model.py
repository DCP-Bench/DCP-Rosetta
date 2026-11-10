# csplib_018_water_bucket: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_018_water_bucket.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_018_water_bucket.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python csplib_018_water_bucket.py csplib_018_water_bucket.json

from paramita.containers import WcnfFormula
from paramita.modelling import (
    And, Bool, DimacsVariablePool, If, Iff, Or, add_to_weighted_container, to_cnf,
)


def create_model(instance):
    """Pour water between buckets, starting from the initial amounts, until every bucket
    holds its goal amount, with as few pours as possible. A pour moves water from one
    bucket into another until the source is empty or the target is full."""
    capacities = instance["capacities"]        # how many pints each bucket holds
    initial_state = instance["initial_state"]  # pints in each bucket at the start
    goal_state = instance["goal_state"]        # pints each bucket must hold at the end
    max_steps = instance["MAX_STEPS"]          # number of states in the reported sequence
    padding_value = instance["PADDING_VALUE"]  # filler for the states after the goal
    n_buckets = len(capacities)

    # levels[i]: the pint amounts bucket i can hold, from empty to full
    levels = [list(range(0, capacities[i] + 1)) for i in range(n_buckets)]
    # padded_levels[i]: the same amounts with the filler value added
    padded_levels = [[padding_value] + levels[i] for i in range(n_buckets)]

    # holds[t][i][v] is true when bucket i holds v pints in state t. The first state is
    # the starting state, so it never shows the filler value.
    holds = [[{v: Bool(f"holds_{t}_{i}_{v}") for v in (levels[i] if t == 0 else padded_levels[i])}
              for i in range(n_buckets)] for t in range(max_steps)]

    constraints = []

    # Each bucket holds exactly one amount in each state.
    for t in range(max_steps):
        for i in range(n_buckets):
            constraints.append(sum(holds[t][i].values()) == 1)

    # The first state is the initial state.
    for i in range(n_buckets):
        constraints.append(holds[0][i][initial_state[i]])

    # at_goal[t] is true when state t is the goal state.
    # reached[t] is true when the goal has been reached in some state up to t.
    at_goal = [Bool(f"at_goal_{t}") for t in range(max_steps)]
    reached = [Bool(f"reached_{t}") for t in range(max_steps)]
    for t in range(max_steps):
        constraints.append(Iff(at_goal[t], And([holds[t][i][goal_state[i]] for i in range(n_buckets)])))
        if t == 0:
            constraints.append(Iff(reached[0], at_goal[0]))
        else:
            constraints.append(Iff(reached[t], Or([reached[t - 1], at_goal[t]])))

    # The goal is reached within max_steps states.
    constraints.append(reached[max_steps - 1])

    # pour[t][i][j] is true when the step into state t pours water from bucket i into bucket j.
    pour = [[{} for _ in range(n_buckets)] for _ in range(max_steps)]
    for t in range(1, max_steps):
        # After the goal is reached, every bucket shows the filler value.
        for i in range(n_buckets):
            constraints.append(Iff(holds[t][i][padding_value], reached[t - 1]))

        # Before the goal is reached, each step is exactly one pour. After it, there is no pour.
        pours = []
        for i in range(n_buckets):
            for j in range(n_buckets):
                if i != j:
                    pour[t][i][j] = Bool(f"pour_{t}_{i}_{j}")
                    pours.append(pour[t][i][j])
        constraints.append(sum(pours) + reached[t - 1] == 1)

        # A pour from bucket i into bucket j moves the smaller of the water in i and the
        # free room in j. The third bucket keeps its water.
        for i in range(n_buckets):
            for j in range(n_buckets):
                if i == j:
                    continue
                k = next(b for b in range(n_buckets) if b not in (i, j))
                for p in levels[i]:
                    for q in levels[j]:
                        moved = min(p, capacities[j] - q)
                        constraints.append(If(And([pour[t][i][j], holds[t - 1][i][p], holds[t - 1][j][q]]),
                                              And([holds[t][i][p - moved], holds[t][j][q + moved]])))
                for r in levels[k]:
                    constraints.append(If(And([pour[t][i][j], holds[t - 1][k][r]]), holds[t][k][r]))

    # cost: the number of transfers, one per pour.
    cost = sum(pour[t][i][j] for t in range(1, max_steps)
               for i in range(n_buckets) for j in range(n_buckets) if i != j)

    # sequence[t][i]: pints in bucket i in state t, or the filler value after the goal.
    sequence = [[sum(v * holds[t][i][v] for v in holds[t][i]) for i in range(n_buckets)]
                for t in range(max_steps)]

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-cost, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the cost of the sequence, minimised (its
    # negation is what the soft clauses maximise).
    return (formula, pool), {"cost": cost, "sequence": sequence}, cost


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
