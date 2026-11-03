# football: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/football.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python football.py

from pysat.card import CardEnc, EncType as CardType
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import EncType as PBType
from pysat.pb import PBEnc


def create_model(instance):
    """Buy football players from four groups (goalkeepers, defenders, midfielders and strikers)
    so that the total price is as close as possible to the GBP 30 million limit without going
    over it, buying at least the required number from each group and at least eleven players
    in total."""
    # Prices are in thousands of pounds, so GBP 30 million is 30000.
    budget = 30000
    prices = [
        [730, 1280, 3880],                                              # goalkeepers
        [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570],                # defenders
        [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130],   # midfielders
        [4460, 6470, 7780, 8390, 9500],                                 # strikers
    ]
    # (fewest, most) players to buy from each group: exactly one goalkeeper, at least two
    # defenders and strikers, at least three midfielders, and no more than the group holds.
    min_max = [[1, 1], [2, 8], [3, 10], [2, 5]]
    min_players = 11

    # (group, index) of every player, and the price of each player.
    players = [(g, k) for g in range(len(prices)) for k in range(len(prices[g]))]
    price = {p: prices[p[0]][p[1]] for p in players}

    # The squad built greedily gives a lower bound on the best spend, which z need not go
    # below. It takes the cheapest players that each group must supply, then the cheapest
    # others up to eleven, then the dearest players that still fit within the budget.
    squad = []
    for g in range(len(prices)):
        squad += sorted((p for p in players if p[0] == g), key=price.get)[:min_max[g][0]]

    # room(p) is true when the group of p can take one more player.
    def room(p):
        return sum(1 for q in squad if q[0] == p[0]) < min_max[p[0]][1]

    for p in sorted(players, key=price.get):
        if len(squad) >= min_players:
            break
        if p not in squad and room(p):
            squad.append(p)
    spend = sum(price[p] for p in squad)
    if spend <= budget and len(squad) >= min_players:
        for p in sorted(players, key=price.get, reverse=True):
            if p not in squad and room(p) and spend + price[p] <= budget:
                squad.append(p)
                spend += price[p]
        lower = spend
    else:
        lower = 0

    pool = IDPool()
    # x[p] is true when player p is bought.
    x = {p: pool.id(("x", p)) for p in players}
    # z is the total price of the players bought, in thousands of pounds, between lower and
    # the budget.
    z = Integer("z", lower, max(budget, lower + 1), vpool=pool)
    engine = IntegerEngine(vars=[z], vpool=pool)
    if budget < lower + 1:
        engine.add_linear(z <= budget)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # Each group buys at least its fewest and at most its most players.
    for g in range(len(prices)):
        group = [x[p] for p in players if p[0] == g]
        formula.extend(CardEnc.atleast(lits=group, bound=min_max[g][0], vpool=pool,
                                       encoding=CardType.seqcounter).clauses)
        if min_max[g][1] < len(group):
            formula.extend(CardEnc.atmost(lits=group, bound=min_max[g][1], vpool=pool,
                                          encoding=CardType.seqcounter).clauses)

    # The squad has at least min_players players in all.
    formula.extend(CardEnc.atleast(lits=list(x.values()), bound=min_players, vpool=pool,
                                   encoding=CardType.seqcounter).clauses)

    # bits holds z - lower in binary, least significant digit first.
    n_bits = max(budget - lower, 1).bit_length()
    bits = [pool.id(("z bit", k)) for k in range(n_bits)]
    # Each value of z sets the bits to its digits.
    for v in range(lower, max(budget, lower + 1) + 1):
        for k in range(n_bits):
            formula.append([-z.equals(v), bits[k] if ((v - lower) >> k) & 1 else -bits[k]])
    # The prices of the players bought add up to lower plus the value of the bits.
    formula.extend(PBEnc.equals(lits=[x[p] for p in players] + bits,
                                weights=[price[p] for p in players]
                                + [-(1 << k) for k in range(n_bits)],
                                bound=lower, vpool=pool, encoding=PBType.adder).clauses)

    # Maximise the spend: a player left out costs their price, so the cost is the total price
    # of the players not bought, which is smallest when the spend is largest.
    for p in players:
        formula.append([x[p]], weight=price[p])

    return formula, {"z": z}


if __name__ == "__main__":
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    formula, outputs = create_model({})

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
