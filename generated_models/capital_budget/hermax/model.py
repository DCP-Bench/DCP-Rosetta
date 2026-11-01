"""
Capital budgeting: maximize NPV subject to budget constraint.

Select a subset of investments to maximize total NPV, such that
total cash flow does not exceed budget.
"""

from hermax.model import Model


def build(instance):
    m = Model()

    budget = instance["budget"]
    npv = instance["npv"]
    cash_flow = instance["cash_flow"]
    n = len(npv)

    # Variable: whether each investment is chosen
    x = m.bool_vector("x", n)

    # Budget constraint: sum of cash flows <= budget
    m &= (sum(cash_flow[i] * x[i] for i in range(n)) <= budget)

    # Objective: maximize NPV
    # Pay weight when literal is false (so we maximize by charging for not taken)
    for i, value in enumerate(npv):
        m.obj[value] += x[i]

    # Total NPV as a linear expression
    z = sum(npv[i] * x[i] for i in range(n))

    return m, {"x": x, "z": z}
