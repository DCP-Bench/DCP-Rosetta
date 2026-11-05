"""Two prices that add up to 120 cents and multiply to 3200 cents squared.

Hexaly satisfies an exact product far more easily when each unknown picks its value from a short list than when it
ranges over every integer: here each price is a divisor of the product, chosen by an index.
"""
import hexaly.optimizer as hx

TOTAL = 120
PRODUCT = 3200
# Each price divides the product, so only its divisors up to the total are possible prices
DIVISORS = [d for d in range(1, TOTAL + 1) if PRODUCT % d == 0]

with hx.HexalyOptimizer() as optimizer:
    optimizer.param.verbosity = 0
    optimizer.param.time_limit = 10
    model = optimizer.model

    table = model.array(DIVISORS)
    choice = [model.int(0, len(DIVISORS) - 1) for _ in range(2)]  # which divisor each price is
    prices = [model.at(table, c) for c in choice]               # the prices themselves

    model.constraint(prices[0] + prices[1] == TOTAL)
    model.constraint(prices[0] * prices[1] == PRODUCT)
    model.minimize(0)  # a feasibility problem still needs an objective
    model.close()
    optimizer.solve()

    status = optimizer.solution.status
    print("Status:", status.name)
    if status in (hx.HxSolutionStatus.FEASIBLE, hx.HxSolutionStatus.OPTIMAL):
        print("Prices:", sorted(p.value for p in prices))
