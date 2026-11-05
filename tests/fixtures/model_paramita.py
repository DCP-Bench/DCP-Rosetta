from paramita.containers import CnfFormula, WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, add_to_container, add_to_weighted_container, to_cnf


def create_model(instance):
    n = instance["n"]
    # x and y each take a value in 0..n as a unary sum of Bools, with the order
    # constraint that a higher Bool is set only when the one below it is.
    xs = [Bool(f"x{i}") for i in range(n)]
    ys = [Bool(f"y{i}") for i in range(n)]
    order = [~xs[i + 1] | xs[i] for i in range(n - 1)] + [~ys[i + 1] | ys[i] for i in range(n - 1)]
    x = sum(xs)
    y = sum(ys)
    pool = DimacsVariablePool()
    if not instance["optimize"]:
        formula = CnfFormula()
        add_to_container(And(order + [x + y == n]), to_cnf, formula, pool)
        return (formula, pool), {"x": x, "y": y}
    # MaxSAT maximises the soft clauses, so a minimisation encodes the negation.
    sense = "minimize"
    objective = -(x + y) if sense.startswith("min") else x + y
    formula = WcnfFormula()
    add_to_weighted_container(objective, And(order + [x + y >= n]), to_cnf, formula, pool)
    # The objective in the problem's terms, which the runner reports.
    return (formula, pool), {"x": x, "y": y}, x + y
