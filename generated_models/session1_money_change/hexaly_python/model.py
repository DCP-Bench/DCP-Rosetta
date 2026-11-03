"""Money change: pay the amount with the available coins, using as few coins as possible."""
import hexaly.optimizer as hx


def build(instance):
    # amount = the change to give; types_of_coins[i] = value of one coin of type i;
    # available_coins[i] = how many coins of type i she has
    amount, values, available = instance["amount"], instance["types_of_coins"], instance["available_coins"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # coin_counts[i] = number of coins of type i given to Bob; the upper bound is the number available
    coin_counts = [model.int(0, a) for a in available]

    # The coins given add up to exactly the amount
    model.constraint(model.sum(v * c for v, c in zip(values, coin_counts)) == amount)

    # Minimise the number of coins used
    model.minimize(model.sum(coin_counts))
    return optimizer, {"coin_counts": coin_counts}
