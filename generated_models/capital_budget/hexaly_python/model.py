"""Capital budgeting: choose investments within the budget so that the total net present value is maximal."""
import hexaly.optimizer as hx


def build(instance):
    # npv[i] = net present value that investment i yields; cash_flow[i] = cash outflow investment i needs now
    # budget = total amount available for investment now
    npv, cash_flow, budget = instance["npv"], instance["cash_flow"], instance["budget"]
    n = len(npv)  # number of investments
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # x[i] = 1 if investment i is chosen
    x = [model.bool() for _ in range(n)]

    # The cash outflow of the chosen investments must fit the budget
    model.constraint(model.sum(cash_flow[i] * x[i] for i in range(n)) <= budget)

    # z is the total NPV of the chosen investments, to be maximised
    z = model.sum(npv[i] * x[i] for i in range(n))
    model.maximize(z)

    return optimizer, {"x": x, "z": z}
