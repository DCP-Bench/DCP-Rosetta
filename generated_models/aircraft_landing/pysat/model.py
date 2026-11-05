# aircraft_landing: a PySAT (Python) model from DCP Rosetta.
# Download the `aircraft_landing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_landing.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python aircraft_landing.py aircraft_landing.json

from math import gcd

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer


def create_model(instance):
    """Aircraft landing on a single runway with a fixed landing order: give every
    aircraft a landing time in its time window, keep the required separation
    between any two landings, and minimise the total penalty for landing before
    or after the target time."""
    earliest = instance["earliest_landing"]      # earliest[i]: start of aircraft i's time window
    latest = instance["latest_landing"]          # latest[i]: end of aircraft i's time window
    target = instance["target_landing"]          # target[i]: preferred landing time of aircraft i
    penalty_after = instance["penalty_after"]    # penalty_after[i]: cost per time unit aircraft i lands after its target
    penalty_before = instance["penalty_before"]  # penalty_before[i]: cost per time unit aircraft i lands before its target
    separation = instance["separation_time"]     # separation[i][j]: minimum time from landing i to a later landing j
    n_aircraft = len(earliest)

    pool = IDPool()

    # The schedule rules as hard clauses, with the penalties added below.
    formula = WCNF()

    def ge(x, v):
        # The statement that x lands at or after time v. True or False when v is outside the window of x.
        if v <= x.lb:
            return True
        if v > x.ub:
            return False
        return x.ge(v)

    def neg(statement):
        # The opposite of a statement from ge. True and False swap.
        return (not statement) if isinstance(statement, bool) else -statement

    def clause(*statements):
        # The rule that at least one of the statements holds. A true statement satisfies it,
        # false ones are dropped, and with none left no schedule meets the rule.
        if any(statement is True for statement in statements):
            return
        kept = [statement for statement in statements if statement is not False]
        if not kept:
            dead = pool.id("infeasible")
            formula.append([dead])
            formula.append([-dead])
            return
        formula.append(kept)

    def penalty_of(i, t):
        # The penalty aircraft i pays for landing at time t.
        return (penalty_before[i] * max(0, target[i] - t)
                + penalty_after[i] * max(0, t - target[i]))

    def add_sum(s, a, b):
        # s is exactly a + b, in steps: a reaching va and b reaching vb makes s reach va + vb,
        # and a and b staying below va + 1 and vb + 1 keep s from reaching more.
        for va in range(0, a.ub + 1):
            for vb in range(0, b.ub + 1):
                if va + vb >= 1:
                    clause(neg(ge(a, va)), neg(ge(b, vb)), ge(s, va + vb))
                clause(ge(a, va + 1), ge(b, vb + 1), neg(ge(s, va + vb + 1)))

    # landing_times[i] is the time aircraft i lands, within its window.
    landing_times = [Integer(f"landing_times_{i}", earliest[i], latest[i],
                             encoding="coupled", vpool=pool) for i in range(n_aircraft)]

    # Each landing time is one time in its window.
    for x in landing_times:
        formula.extend(x.domain_clauses())

    # Aircraft j lands at least separation[i][j] after aircraft i, for every i before j.
    # For each time t, if i lands at or after t, then j lands at or after t plus that separation.
    for i in range(n_aircraft):
        for j in range(i + 1, n_aircraft):
            gap = separation[i][j]
            for t in range(earliest[i], latest[i] + 1):
                clause(neg(ge(landing_times[i], t)), ge(landing_times[j], t + gap))

    # Penalty. Each time unit an aircraft lands before its target costs penalty_before: for each
    # time t from its window start up to the target, that cost is paid unless the aircraft lands
    # at or after t. Each time unit after the target costs penalty_after: for each time t after
    # the target, up to the window end, the cost is paid when the aircraft lands at or after t.
    for i in range(n_aircraft):
        x = landing_times[i]
        for t in range(earliest[i] + 1, min(target[i], latest[i]) + 1):
            if penalty_before[i] > 0:
                formula.append([x.ge(t)], weight=penalty_before[i])
        for t in range(max(target[i], earliest[i]) + 1, latest[i] + 1):
            if penalty_after[i] > 0:
                formula.append([-x.ge(t)], weight=penalty_after[i])

    # greedy_times[j] is the earliest time aircraft j can land if it lands as early as its window
    # start and target allow and keeps the separations from earlier aircraft.
    greedy_times = []
    for j in range(n_aircraft):
        t = max([earliest[j], target[j]] + [greedy_times[i] + separation[i][j] for i in range(j)])
        greedy_times.append(t)

    # Upper bound on the total penalty. The penalty of the greedy schedule is used when it fits
    # every window. Otherwise each aircraft's worse window end is added. No optimal schedule
    # costs more than this bound.
    if all(greedy_times[i] <= latest[i] for i in range(n_aircraft)):
        upper = sum(penalty_of(i, greedy_times[i]) for i in range(n_aircraft))
    else:
        upper = sum(max(penalty_of(i, earliest[i]), penalty_of(i, latest[i])) for i in range(n_aircraft))

    # The penalty rates share the divisor unit, so penalties are counted in steps of unit. This keeps
    # the counts small.
    unit = 0
    for rate in list(penalty_before) + list(penalty_after):
        unit = gcd(unit, rate)
    unit = unit or 1
    # The largest total, in steps of unit.
    max_steps = upper // unit

    # cost[i] is the penalty of aircraft i in steps of unit. It reaches k steps exactly when aircraft i
    # lands at least the time needed for k steps before its target, or at least the time needed for k
    # steps after it. A penalty above max_steps is ruled out.
    cost = []
    for i in range(n_aircraft):
        x = landing_times[i]
        worst = max(penalty_of(i, earliest[i]), penalty_of(i, latest[i])) // unit  # the largest penalty in steps
        cost_i = Integer(f"cost_{i}", 0, min(worst, max_steps), encoding="order", vpool=pool)
        formula.extend(cost_i.domain_clauses())
        for k in range(1, min(worst, max_steps + 1) + 1):
            early = False
            if penalty_before[i] > 0:
                early_time = -(-k * unit // penalty_before[i])
                early = neg(ge(x, target[i] - early_time + 1))
            late = False
            if penalty_after[i] > 0:
                late_time = -(-k * unit // penalty_after[i])
                late = ge(x, target[i] + late_time)
            reaches_k = ge(cost_i, k)
            clause(neg(early), reaches_k)
            clause(neg(late), reaches_k)
            clause(neg(reaches_k), early, late)
        cost.append(cost_i)

    # total_so_far is the penalty of the aircraft so far, in steps of unit. Adding each aircraft in turn
    # gives the total over all aircraft.
    total_so_far = cost[0]
    for j in range(1, n_aircraft):
        top = min(max_steps, total_so_far.ub + cost[j].ub)
        running = Integer(f"total_{j}", 0, top, encoding="order", vpool=pool)
        formula.extend(running.domain_clauses())
        add_sum(running, total_so_far, cost[j])
        total_so_far = running

    # total_penalty is the total penalty in units of 1, which is unit times the total in steps.
    total_penalty = Integer("total_penalty", 0, unit * total_so_far.ub, encoding="coupled", vpool=pool)
    formula.extend(total_penalty.domain_clauses())
    for v in range(1, unit * total_so_far.ub + 1):
        steps = -(-v // unit)
        clause(neg(total_penalty.ge(v)), ge(total_so_far, steps))
        clause(neg(ge(total_so_far, steps)), total_penalty.ge(v))

    # The objective in the problem's terms: the total penalty (RC2's cost is the same
    # penalty, paid per time unit away from each target).
    return formula, {"landing_times": landing_times, "total_penalty": total_penalty}, total_penalty


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs, objective = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
