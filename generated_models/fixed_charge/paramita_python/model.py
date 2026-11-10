# fixed_charge: a Paramita (Python) model from DCP Rosetta.
# Download the `fixed_charge.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fixed_charge.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python fixed_charge.py fixed_charge.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, If, add_to_weighted_container, to_cnf


def create_model(instance):
    """A company makes shirts, shorts and pants. Each product needs labor and
    cloth from limited capacities, and can only be made on a machine the company
    rents at a fixed cost. Choose the machines to rent and how much of each
    product to make, to maximize the profit after the renting costs."""
    num_products = instance["num_products"]      # the number of products
    num_machines = instance["num_machines"]      # the number of machines
    resources = instance["resources"]            # the resources, labor and cloth
    capacity = instance["capacity"]              # capacity[r]: the amount of resource r the company has
    use = instance["use"]                        # use[p][r]: the amount of resource r that one unit of product p needs
    max_production = instance["max_production"]  # the most units of any one product
    renting_cost = instance["renting_cost"]      # renting_cost[m]: the cost of renting machine m
    profit = [instance["product"][p][0] for p in range(num_products)]      # profit[p]: profit per unit of product p, before renting
    machine_of = [instance["product"][p][1] for p in range(num_products)]  # machine_of[p]: the machine product p needs

    # max_units[p]: the most units of product p that the resources allow, and at most max_production
    max_units = []
    for p in range(num_products):
        bound = max_production
        for r in resources:
            if use[p][r] > 0:
                bound = min(bound, capacity[r] // use[p][r])
        max_units.append(bound)

    # bits[p][k] is true when 2 ** k is counted in the units of product p
    bits = [[Bool(f"units_{p}_bit_{k}") for k in range(max(max_units[p], 1).bit_length())]
            for p in range(num_products)]
    # units[p] is the number of units of product p made
    units = [sum(2 ** k * b for k, b in enumerate(bits[p])) for p in range(num_products)]
    # rent[m] is true when machine m is rented
    rent = [Bool(f"rent_{m}") for m in range(num_machines)]
    constraints = []

    # The units made of each product stay within its limit.
    for p in range(num_products):
        constraints.append(units[p] <= max_units[p])

    # The products made use no more of each resource than the company has.
    for r in resources:
        constraints.append(sum(use[p][r] * units[p] for p in range(num_products)) <= capacity[r])

    # A product can only be made when its machine is rented.
    for p in range(num_products):
        constraints.append(If(units[p] >= 1, rent[machine_of[p]]))

    # The profit on the products, minus the renting costs of the rented machines.
    z = sum(profit[p] * units[p] for p in range(num_products)) \
        - sum(renting_cost[m] * rent[m] for m in range(num_machines))

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # maximise as soft clauses. The pool gives each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(z, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the profit minus the renting costs,
    # maximised (the soft clauses maximise it).
    return (formula, pool), {"z": z}, z


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
