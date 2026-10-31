from hermax.model import Model

# Prices in GBP thousands, from the problem description (GBP millions times 1000).
GOALKEEPERS = [730, 1280, 3880]
DEFENDERS = [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570]
MIDFIELDERS = [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130]
STRIKERS = [4460, 6470, 7780, 8390, 9500]
LIMIT = 30000  # GBP 30 million chairman's limit, in thousands


def build(instance):
    m = Model()
    g = m.bool_vector("g", len(GOALKEEPERS))
    d = m.bool_vector("d", len(DEFENDERS))
    mid = m.bool_vector("m", len(MIDFIELDERS))
    s = m.bool_vector("s", len(STRIKERS))

    # Must buy 1 goalkeeper exactly.
    m &= (sum(g) == 1)
    # Must buy 2 or more defenders.
    m &= (sum(d) >= 2)
    # Must buy 3 or more midfielders.
    m &= (sum(mid) >= 3)
    # Must buy 2 or more strikers.
    m &= (sum(s) >= 2)
    # Must buy at least eleven players in total.
    m &= (sum(g) + sum(d) + sum(mid) + sum(s) >= 11)

    # Total price stays within the limit.
    price_terms = (
        [(p, g[i]) for i, p in enumerate(GOALKEEPERS)]
        + [(p, d[i]) for i, p in enumerate(DEFENDERS)]
        + [(p, mid[i]) for i, p in enumerate(MIDFIELDERS)]
        + [(p, s[i]) for i, p in enumerate(STRIKERS)]
    )
    total = sum(p * b for p, b in price_terms)
    m &= (total <= LIMIT)

    # Spend as much as possible: minimise the negated total.
    m.obj += 0 - total

    return m, {"z": total}
