"""
Model for csplib_010_social_golfers_problem.

Schedule golfers to play in groups each week such that no two golfers
play in the same group more than once.

Constraints:
1. Each week, golfers are divided into n_groups groups of group_size each
2. No pair of golfers meets in the same group more than once across weeks
"""
from hermax.model import Model


def build(instance):
    n_weeks = instance["n_weeks"]
    n_groups = instance["n_groups"]
    group_size = instance["group_size"]
    n_golfers = n_groups * group_size

    m = Model()

    # Decision variable: assign[golfer][week] = group number (0 to n_groups-1)
    assign = m.int_matrix("assign", n_golfers, n_weeks, 0, n_groups - 1)

    # Constraint: Each group in each week has exactly group_size golfers
    # For each week and group, count golfers assigned to that group
    for w in range(n_weeks):
        for g in range(n_groups):
            # Use all-different-like constraint: for each position in the group,
            # exactly group_size golfers should have assign[golfer][w] == g
            # We count by creating a sum of boolean variables
            golfers_in_group = [m.bool(f"in_group_{w}_{g}_{golfer}")
                               for golfer in range(n_golfers)]
            for golfer in range(n_golfers):
                # golfers_in_group[golfer] is true iff assign[golfer][w] == g
                m &= (golfers_in_group[golfer] == (assign[golfer][w] == g))
            # Sum of booleans should equal group_size
            m &= (sum(golfers_in_group) == group_size)

    # Constraint: No pair of golfers meets in the same group more than once
    for g1 in range(n_golfers):
        for g2 in range(g1 + 1, n_golfers):
            # Create auxiliary booleans for each week: do they meet in week w?
            meet_bools = [m.bool(f"meet_{g1}_{g2}_week{w}") for w in range(n_weeks)]
            for w in range(n_weeks):
                # They meet in week w if assign[g1][w] == assign[g2][w]
                m &= (meet_bools[w] == (assign[g1][w] == assign[g2][w]))
            # They can meet in at most 1 week
            m &= (sum(meet_bools) <= 1)

    return m, {"assign": assign}
