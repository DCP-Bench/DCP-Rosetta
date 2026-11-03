"""Social golfers: schedule groups for several weeks so that no two golfers play together more than once."""
import hexaly.optimizer as hx


def build(instance):
    weeks, groups, size = instance["n_weeks"], instance["n_groups"], instance["group_size"]
    golfers = groups * size
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # members[w][g] is the set of golfers in group g of week w. Set decisions let Hexaly move
    # golfers between groups directly, which its search handles better than integer labels.
    members = [[model.set(golfers) for _ in range(groups)] for _ in range(weeks)]

    for w in range(weeks):
        # Every golfer plays in exactly one group each week
        model.constraint(model.partition(*members[w]))
        # Every group has exactly group_size golfers
        for g in range(groups):
            model.constraint(model.count(members[w][g]) == size)
    # No two golfers share a group in more than one week: two groups of different weeks have
    # at most one golfer in common
    for w1 in range(weeks):
        for w2 in range(w1 + 1, weeks):
            for g1 in range(groups):
                for g2 in range(groups):
                    model.constraint(model.count(model.intersection(members[w1][g1], members[w2][g2])) <= 1)

    # assign[i][w] is the group (0-based) of golfer i in week w
    assign = [[model.sum(g * model.contains(members[w][g], i) for g in range(groups)) for w in range(weeks)]
              for i in range(golfers)]
    return optimizer, {"assign": assign}
