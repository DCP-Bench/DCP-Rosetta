"""Social golfers: schedule groups for several weeks so that no two golfers play together more than once."""
import hexaly.optimizer as hx


def build(instance):
    # n_weeks = weeks in the schedule; n_groups = groups playing each week; group_size = golfers per group
    weeks, groups, size = instance["n_weeks"], instance["n_groups"], instance["group_size"]
    golfers = groups * size  # every golfer plays once a week, so there are n_groups * group_size golfers
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # members[w][g] = the set of golfers (numbered 0..golfers-1) who play in group g in week w.
    # Set decisions let Hexaly move golfers between groups directly.
    members = [[model.set(golfers) for _ in range(groups)] for _ in range(weeks)]

    for w in range(weeks):
        # Each golfer plays once a week: the groups of a week split all golfers, each golfer in exactly one group
        model.constraint(model.partition(*members[w]))
        # Golfers always play in groups of the same size: every group has exactly group_size golfers
        for g in range(groups):
            model.constraint(model.count(members[w][g]) == size)
    # No golfer plays in the same group as any other golfer on more than one occasion: two groups
    # of different weeks have at most one golfer in common
    for w1 in range(weeks):
        for w2 in range(w1 + 1, weeks):
            for g1 in range(groups):
                for g2 in range(groups):
                    model.constraint(model.count(model.intersection(members[w1][g1], members[w2][g2])) <= 1)

    # assign[i][w] is the group (0-based) of golfer i in week w; the output, read off the sets above
    assign = [[model.sum(g * model.contains(members[w][g], i) for g in range(groups)) for w in range(weeks)]
              for i in range(golfers)]
    return optimizer, {"assign": assign}
