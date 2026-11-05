# aircraft_landing: a Paramita (Python) model from DCP Rosetta.
# Download the `aircraft_landing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_landing.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python aircraft_landing.py aircraft_landing.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, add_to_weighted_container, to_cnf


# The whole number written with the named digits name_0, name_1, ... (lowest digit first).
def whole_number(name, n_digits):
    return sum((1 << k) * Bool(f"{name}_{k}") for k in range(n_digits))


# The number of digits needed to write every whole number from 0 to max_value.
def digits_needed(max_value):
    return max(max_value, 0).bit_length()


def create_model(instance):
    """Aircraft landing on a single runway with a fixed landing order: give every
    aircraft a landing time in its time window, keep the required separation
    between landings, and minimise the penalty for landing before or after the
    target time."""
    earliest = instance["earliest_landing"]      # earliest[i]: start of aircraft i's time window
    latest = instance["latest_landing"]          # latest[i]: end of aircraft i's time window
    target = instance["target_landing"]          # target[i]: preferred landing time of aircraft i
    penalty_before = instance["penalty_before"]  # penalty_before[i]: cost per time unit aircraft i lands before its target
    penalty_after = instance["penalty_after"]    # penalty_after[i]: cost per time unit aircraft i lands after its target
    separation = instance["separation_time"]     # separation[i][j]: minimum time between landing i and landing j
    n_aircraft = len(target)                     # the number of aircraft

    # The constraints of the schedule.
    constraints = []
    # landing[i] is the time at which aircraft i lands.
    landing = []
    # penalty[i] is what aircraft i pays for landing before or after its target.
    penalty = []

    for i in range(n_aircraft):
        # The landing time is earliest[i] plus an offset, which runs up to the window width.
        width = latest[i] - earliest[i]
        offset = whole_number(f"offset_{i}", digits_needed(width))
        landing.append(earliest[i] + offset)
        # The offset stays within the window, so the landing is no later than the window end.
        if (1 << digits_needed(width)) - 1 > width:
            constraints.append(offset <= width)

        # early is how many time units aircraft i lands before its target (0 if it cannot).
        early_max = max(0, target[i] - earliest[i])
        if early_max > 0:
            early = whole_number(f"early_{i}", digits_needed(early_max))
            # The earliness covers the gap between the target and the landing time.
            constraints.append(early >= target[i] - landing[i])
        else:
            early = 0

        # late is how many time units aircraft i lands after its target (0 if it cannot).
        late_max = max(0, latest[i] - target[i])
        if late_max > 0:
            late = whole_number(f"late_{i}", digits_needed(late_max))
            # The lateness covers the gap between the landing time and the target.
            constraints.append(late >= landing[i] - target[i])
        else:
            late = 0

        penalty.append(penalty_before[i] * early + penalty_after[i] * late)

    # Aircraft land in the order of their index, each at least the separation after the one before.
    for i in range(n_aircraft):
        for j in range(i + 1, n_aircraft):
            constraints.append(landing[j] >= landing[i] + separation[i][j])

    # The total penalty over all aircraft, to minimise.
    total_penalty = sum(penalty)

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-total_penalty, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the total penalty, minimised (its negation is
    # what the soft clauses maximise).
    return (formula, pool), {"landing_times": landing, "total_penalty": total_penalty}, total_penalty


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
