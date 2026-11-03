# bananas: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bananas.html
# Run it (after `pip install cpmpy`) with:
#   python bananas.py

import cpmpy as cp


def create_model(instance):
    """Buy 100 fruits for 100 dollars, at least one of each kind: bananas cost 3
    dollars for 5, oranges 5 dollars for 7, mangoes 7 dollars for 9 and apples
    9 dollars for 3. Bananas and apples are disliked, so buy as few of them as possible."""
    # The problem statement fixes all prices, so nothing is read from instance.
    # Prices are in 1/945 dollar (945 = 5*7*9*3 clears the fractions):
    # banana 3/5 = 567, orange 5/7 = 675, mango 7/9 = 735, apple 9/3 = 2835.
    prices = [567, 675, 735, 2835]

    # x[k] is the number of fruits bought of kind k: banana, orange, mango, apple
    x = cp.intvar(1, 100, shape=4, name="x")
    bananas, oranges, mangoes, apples = x

    model = cp.Model()
    # 100 fruits in total.
    model.add(cp.sum(x) == 100)
    # They cost exactly 100 dollars.
    model.add(cp.sum(x * prices) == 100 * 945)
    # Buy as few bananas and apples as possible.
    model.minimize(bananas + apples)

    return model, {"bananas": bananas, "oranges": oranges, "mangoes": mangoes, "apples": apples}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
