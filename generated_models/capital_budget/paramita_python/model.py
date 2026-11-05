# capital_budget: a Paramita (Python) model from DCP Rosetta.
# Download the `capital_budget.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/capital_budget.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python capital_budget.py capital_budget.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, add_to_weighted_container, to_cnf


def create_model(instance):
    """A company considers a number of investments, each with a net present value (NPV) and a
    cash outflow now. Choose the investments that maximise the total NPV within the total
    budget."""
    budget = instance["budget"]        # the total cash available for investment now
    npv = instance["npv"]              # npv[i] is the net present value of investment i
    cash_flow = instance["cash_flow"]  # cash_flow[i] is the cash outflow investment i needs now
    n_investments = len(npv)

    # x[i] is true when investment i is chosen
    x = [Bool(f"x_{i}") for i in range(n_investments)]

    constraints = []  # the rules of the choice

    # The cash outflow of the chosen investments stays within the budget.
    constraints.append(sum(cash_flow[i] * x[i] for i in range(n_investments)) <= budget)

    # z is the total NPV of the chosen investments. The company maximises it.
    z = sum(npv[i] * x[i] for i in range(n_investments))

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # maximise as soft clauses. The pool gives each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(z, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the total NPV of the chosen investments,
    # maximised (the soft clauses maximise it).
    return (formula, pool), {"x": x, "z": z}, z


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs, objective = create_model(instances[index])

    solver = MaxSatSolver.from_name("EvalMaxSAT2022")
    # copy the formula into the solver: the hard clauses, then each soft clause with its weight
    solver.add_clauses(formula.hard_clauses())
    for weight, clause in formula.soft_clauses():
        solver.add_clause(clause, weight)

    if solver.solve() == MAXSAT_ANSWER.OPTIMAL:
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
        print("objective =", evaluate(objective, truth))
    else:
        print("No solution")
