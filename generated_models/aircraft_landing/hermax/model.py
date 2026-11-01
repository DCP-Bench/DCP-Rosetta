from hermax.model import Model


def build(instance):
    # Extract instance data
    earliest = instance["earliest_landing"]
    latest = instance["latest_landing"]
    target = instance["target_landing"]
    penalty_before = instance["penalty_before"]
    penalty_after = instance["penalty_after"]
    separation = instance["separation_time"]

    n_aircraft = len(earliest)

    # Create model and variables
    m = Model()
    # Each aircraft i can land between earliest[i] and latest[i]
    landing_times = m.int_vector(
        "landing_time",
        n_aircraft,
        min(earliest),
        max(latest)
    )

    # Time window constraints: earliest_landing[i] <= landing_times[i] <= latest_landing[i]
    for i in range(n_aircraft):
        m &= (landing_times[i] >= earliest[i])
        m &= (landing_times[i] <= latest[i])

    # Separation constraints: landing_times[i] + separation_time[i][j] <= landing_times[j]
    # Since aircraft land in a fixed sequence, separation only applies when i < j
    for i in range(n_aircraft):
        for j in range(i + 1, n_aircraft):
            m &= (landing_times[i] + separation[i][j] <= landing_times[j])

    # Objective: minimize total penalty
    # For each aircraft i, compute penalty based on early or late landing
    # Penalty = penalty_before[i] * max(0, target[i] - landing_times[i])
    #         + penalty_after[i] * max(0, landing_times[i] - target[i])
    # Minimize sum of all penalties

    # Build objective: minimize sum of penalties
    # Use soft clauses: for each (aircraft, time) pair, pay the penalty when NOT landing at that time
    total_cost_expr = 0

    for i in range(n_aircraft):
        # For each possible landing time t for aircraft i
        for t in range(earliest[i], latest[i] + 1):
            # Calculate penalty for landing at time t
            if t < target[i]:
                # Landing early: penalty = penalty_before[i] * (target[i] - t)
                cost = penalty_before[i] * (target[i] - t)
            elif t > target[i]:
                # Landing late: penalty = penalty_after[i] * (t - target[i])
                cost = penalty_after[i] * (t - target[i])
            else:
                # Landing on target: penalty = 0
                cost = 0

            # Add cost to expression if non-zero
            # We pay cost when landing_times[i] == t (so use negation in soft clause)
            if cost > 0:
                total_cost_expr += cost * (landing_times[i] == t)

    # Add objective as soft clauses: pay when the equality is false (i.e., DON'T land at that time)
    # This means for each (aircraft, time) pair with cost > 0, we're paying that cost
    # multiplied by a boolean expression. We need to negate this.
    m.obj += total_cost_expr

    return m, {
        "landing_times": landing_times,
        "total_penalty": total_cost_expr
    }
