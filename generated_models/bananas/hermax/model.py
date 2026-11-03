# bananas: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bananas.html
# Run it (after `pip install hermax`) with:
#   python bananas.py

from hermax.model import Model, sum_expr


def create_model(instance):
    """Buy 100 fruits for 100 dollars, where five bananas cost 3 dollars, seven oranges
    5 dollars, nine mangoes 7 dollars and three apples 9 dollars. Every kind of fruit
    must be bought at least once, and the number of bananas plus apples should be as
    small as possible."""
    # The statement fixes every number here, so the instance carries no data to read.
    total_fruits = 100   # the number of fruits to buy
    total_dollars = 100  # the amount of money to spend

    # Prices per fruit are 3/5, 5/7, 7/9 and 3 dollars. Measuring money in units of 1/315 dollar,
    # where 315 = lcm(5, 7, 9) is the smallest unit that makes every price per fruit whole,
    # gives bananas 189 units, oranges 225, mangoes 245, apples 945, and 100 dollars is 31500 units.
    unit = 315  # lcm of the denominators 5, 7, 9
    bananas_units = 3 * unit // 5
    oranges_units = 5 * unit // 7
    mangoes_units = 7 * unit // 9
    apples_units = 3 * unit
    budget_units = total_dollars * unit

    m = Model()

    # The number of each fruit bought, at least one of every kind and at most all the fruits.
    bananas = m.int("bananas", 1, total_fruits)  # bananas bought
    oranges = m.int("oranges", 1, total_fruits)  # oranges bought
    mangoes = m.int("mangoes", 1, total_fruits)  # mangoes bought
    apples = m.int("apples", 1, total_fruits)    # apples bought

    # Buy exactly 100 fruits in all.
    m &= (sum_expr([bananas, oranges, mangoes, apples]) == total_fruits)

    # Spend exactly 100 dollars, written in the units of 1/315 dollar per fruit.
    m &= (sum_expr([bananas_units * bananas, oranges_units * oranges,
                    mangoes_units * mangoes, apples_units * apples]) == budget_units)

    # Minimise the bananas and apples bought, which are the fruits the buyer does not like.
    m.obj += sum_expr([bananas, apples])

    return m, {"apples": apples, "bananas": bananas, "mangoes": mangoes, "oranges": oranges}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
