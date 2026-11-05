"""Football: buy players for as close to GBP 30 million as possible, without going over, meeting the position minimums."""
import hexaly.optimizer as hx

# Prices in GBP thousands (the statement gives millions), by position, in the order of the statement
GOALKEEPERS = [730, 1280, 3880]
DEFENDERS = [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570]
MIDFIELDERS = [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130]
STRIKERS = [4460, 6470, 7780, 8390, 9500]
BUDGET = 30000


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # bought[position][i] = 1 if the i-th player of that position is bought
    bought = {name: [model.bool() for _ in prices] for name, prices in
              (("g", GOALKEEPERS), ("d", DEFENDERS), ("m", MIDFIELDERS), ("s", STRIKERS))}

    # Exactly one goalkeeper, at least two defenders, three midfielders and two strikers
    model.constraint(model.sum(bought["g"]) == 1)
    model.constraint(model.sum(bought["d"]) >= 2)
    model.constraint(model.sum(bought["m"]) >= 3)
    model.constraint(model.sum(bought["s"]) >= 2)
    # At least eleven players in total
    model.constraint(model.sum(b for group in bought.values() for b in group) >= 11)

    # The total price in thousands stays within the budget; spend as much as possible
    z = model.sum(price * b for prices, group in ((GOALKEEPERS, bought["g"]), (DEFENDERS, bought["d"]),
                                                  (MIDFIELDERS, bought["m"]), (STRIKERS, bought["s"]))
                  for price, b in zip(prices, group))
    model.constraint(z <= BUDGET)  # the total price never goes over the GBP 30 million limit
    model.maximize(z)  # spend as much of it as possible
    return optimizer, {"z": z}
