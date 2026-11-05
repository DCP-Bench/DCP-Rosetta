# cabling: a Paramita (Python) model from DCP Rosetta.
# Download the `cabling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cabling.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python cabling.py cabling.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, If, add_to_weighted_container, to_cnf


def create_model(instance):
    """n_devices devices are set one above another in a rack, one device per slot. Some pairs
    of devices are joined by one or more cables, and a cable is as long as the number of slots
    between its two devices. Order the devices so that the sum of all cable lengths is as short
    as possible."""
    n_devices = instance["n"]          # the number of devices, and of rack slots
    devices = instance["devices"]      # the names of the devices
    cables = instance["cable_struct"]  # each cable link joins two devices with a number of cables

    # index[name] is the position of the device with that name in devices
    index = {name: i for i, name in enumerate(devices)}
    # place[d][k] is true when device d sits in slot k
    place = [[Bool(f"place_{d}_{k}") for k in range(n_devices)] for d in range(n_devices)]
    # all constraints of the model
    cons = []

    # Each device sits in exactly one slot.
    for d in range(n_devices):
        cons.append(sum(place[d]) == 1)
    # Each slot holds exactly one device.
    for k in range(n_devices):
        cons.append(sum(place[d][k] for d in range(n_devices)) == 1)

    # pos[d] is the slot of device d, as an integer.
    pos = [sum(k * place[d][k] for k in range(n_devices)) for d in range(n_devices)]

    # total is the sum of all cable lengths, built up one cable link at a time.
    total = 0
    for c, (a_name, b_name, count) in enumerate(cables):
        a, b = index[a_name], index[b_name]
        # at_least[m] is true when a cable of this link is at least m + 1 slots long
        at_least = [Bool(f"len_{c}_ge_{m + 1}") for m in range(n_devices - 1)]
        for m in range(n_devices - 2):
            cons.append(If(at_least[m + 1], at_least[m]))
        # length is the number of slots between the two devices, the length of one cable of this link
        length = sum(at_least)
        # A cable is at least as long as the slot gap between its devices, in either direction.
        # Minimising the total pushes each length down to that gap.
        cons.append(pos[a] - pos[b] <= length)
        cons.append(pos[b] - pos[a] <= length)
        total = total + count * length

    # The sum of all cable lengths, the output and the objective.
    final_sum = total

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-final_sum, And(cons), to_cnf, formula, pool)

    # The objective in the problem's terms: the total cable length, minimised (its
    # negation is what the soft clauses maximise).
    return (formula, pool), {"final_sum": final_sum}, final_sum


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
