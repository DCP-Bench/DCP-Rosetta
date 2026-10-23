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
    for w in range(n_weeks):
        for g in range(n_groups):
            # Count how many golfers are in group g in week w
            count_in_group = sum((assign[golfer][w] == g) for golfer in range(n_golfers))
            m &= (count_in_group == group_size)

    # Constraint: No pair of golfers meets in the same group more than once
    for g1 in range(n_golfers):
        for g2 in range(g1 + 1, n_golfers):
            # Count how many weeks g1 and g2 are in the same group
            meetings = sum((assign[g1][w] == assign[g2][w]) for w in range(n_weeks))
            m &= (meetings <= 1)

    return m, {"assign": assign}
