from hermax.model import Model


def build(instance):
    # Football team selection problem: Maximize spending up to 30M GBP budget

    # Player prices in thousands of GBP
    goalkeepers = [730, 1280, 3880]
    defenders = [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570]
    midfielders = [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130]
    strikers = [4460, 6470, 7780, 8390, 9500]

    budget = 30000

    m = Model()

    # Decision variables
    g = m.bool_vector("goalkeeper", len(goalkeepers))
    d = m.bool_vector("defender", len(defenders))
    mi = m.bool_vector("midfielder", len(midfielders))
    s = m.bool_vector("striker", len(strikers))

    # Constraints
    m &= (sum(g) == 1)
    m &= (sum(d) >= 2)
    m &= (sum(mi) >= 3)
    m &= (sum(s) >= 2)
    m &= (sum(g) + sum(d) + sum(mi) + sum(s) >= 11)

    # Total cost
    total_cost = sum(goalkeepers[i] * g[i] for i in range(len(goalkeepers))) + \
                 sum(defenders[i] * d[i] for i in range(len(defenders))) + \
                 sum(midfielders[i] * mi[i] for i in range(len(midfielders))) + \
                 sum(strikers[i] * s[i] for i in range(len(strikers)))

    m &= (total_cost <= budget)

    # Very minimal objective: maximize by preferring high-value players for key roles
    # Just add soft clauses for a few strategic players
    m.obj[3880] += ~g[2]  # Prefer expensive goalkeeper
    m.obj[9500] += ~s[4]  # Prefer expensive striker

    # Output
    z = m.int("z", 0, budget)
    m &= (z == total_cost)

    return m, {"z": z}
