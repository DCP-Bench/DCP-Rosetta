# fancy_dress: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fancy_dress.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python fancy_dress.py

from docplex.mp.model import Model


def create_model(instance):
    """Fancy dress: Mr Greenguest owns a green shirt and can buy a green tie ($10), hat ($2) and
    socks ($12), or pay an $11 entrance fee if not dressed by the rules. Find his cheapest way in."""
    tie_price, hat_price, socks_price = 10, 2, 12  # what he pays to buy each item
    entrance_fee = 11  # paid when not dressed according to rules 1-3

    model = Model("fancy_dress")

    t = model.binary_var(name="t")  # wears a green tie
    h = model.binary_var(name="h")  # wears a green hat
    r = model.binary_var(name="r")  # wears a green shirt
    s = model.binary_var(name="s")  # wears green socks
    n = model.binary_var(name="n")  # pays the entrance fee

    # Each rule may be broken only by paying the fee (rule 4). The rules are clauses over
    # the 0/1 choices, written as "at least one literal holds".
    # 1. A green tie requires a green shirt: not t, or r, or the fee.
    model.add_constraint((1 - t) + r + n >= 1)
    # 2. Green socks or a green shirt only with a green tie or a green hat:
    #    (s or r) -> (t or h), or the fee; one clause for s and one for r.
    model.add_constraint((1 - s) + t + h + n >= 1)
    model.add_constraint((1 - r) + t + h + n >= 1)
    # 3. A green shirt, or a green hat, or no green socks requires a green tie:
    #    (r or h or not s) -> t, or the fee; one clause for each of the three cases.
    model.add_constraint((1 - r) + t + n >= 1)
    model.add_constraint((1 - h) + t + n >= 1)
    model.add_constraint(s + t + n >= 1)

    # Minimise what he pays (he already owns the shirt).
    model.minimize(tie_price * t + hat_price * h + socks_price * s + entrance_fee * n)

    return model, {"t": t, "h": h, "r": r, "s": s, "n": n}


if __name__ == "__main__":
    model, outputs = create_model({})
    model.parameters.mip.tolerances.mipgap = 0  # prove the optimum; the default stops within 0.01% of it
    solution = model.solve()

    if solution:  # a proven optimum
        print("Objective value:", round(solution.objective_value))

        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
