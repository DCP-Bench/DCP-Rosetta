# bananas: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bananas.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python bananas.py

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine

FRUITS = 100   # fruits to buy
DOLLARS = 100  # dollars to spend
UNITS = 315    # one unit is 1/315 dollar; 315 is the least common multiple of 5, 7 and 9


def create_model(instance):
    """Buy 100 fruits for 100 dollars, at least one of each kind: bananas cost 3
    dollars for 5, oranges 5 dollars for 7, mangoes 7 dollars for 9 and apples
    9 dollars for 3. Bananas and apples are disliked, so buy as few of them as possible."""
    # Price of one fruit of each kind, in units.
    price_banana = UNITS * 3 // 5
    price_orange = UNITS * 5 // 7
    price_mango = UNITS * 7 // 9
    price_apple = UNITS * 9 // 3
    budget = DOLLARS * UNITS  # 100 dollars in units

    pool = IDPool()

    # Number of bananas, oranges, mangoes and apples bought, at least one of each.
    bananas, oranges, mangoes, apples = (
        Integer(name, 1, FRUITS, encoding="coupled", vpool=pool)
        for name in ("bananas", "oranges", "mangoes", "apples"))
    engine = IntegerEngine(vars=[bananas, oranges, mangoes, apples], vpool=pool)

    # 100 fruits are bought in all.
    engine.add_linear(bananas + oranges + mangoes + apples == FRUITS)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # The fruits cost exactly the budget. Once the apples and the mangoes are fixed, the
    # oranges make up the rest of the fruits, and each banana bought in place of an orange
    # changes the cost by per_banana units. So the apples and mangoes fix the bananas count,
    # if any bananas count pays the budget exactly. A pair of apple and mango counts with no
    # such bananas count is ruled out.
    per_banana = price_banana - price_orange  # cost change of one banana in place of an orange
    for apple_count in range(1, FRUITS + 1):
        for mango_count in range(1, FRUITS + 1):
            # Units left for the bananas once the oranges, mangoes and apples are paid for.
            left_over = (budget - price_orange * (FRUITS - mango_count - apple_count)
                         - price_mango * mango_count - price_apple * apple_count)
            pair = [-apples.equals(apple_count), -mangoes.equals(mango_count)]
            if left_over % per_banana == 0 and 1 <= left_over // per_banana <= FRUITS:
                formula.append(pair + [bananas.equals(left_over // per_banana)])
            else:
                formula.append(pair)

    # Each banana and each apple bought beyond the first costs 1, so the cost is
    # bananas + apples - 2.
    for fruit in (bananas, apples):
        for v in range(2, FRUITS + 1):
            formula.append([-fruit.ge(v)], weight=1)

    # The objective in the problem's terms: the number of bananas plus apples (RC2's cost is
    # that number minus 2).
    return formula, {"bananas": bananas, "oranges": oranges, "mangoes": mangoes, "apples": apples}, bananas + apples


if __name__ == "__main__":
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    formula, outputs, objective = create_model({})

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
