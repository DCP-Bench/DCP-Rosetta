# session3_kidney_exchange: a Paramita (Python) model from DCP Rosetta.
# Download the `session3_kidney_exchange.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_kidney_exchange.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python session3_kidney_exchange.py session3_kidney_exchange.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, add_to_weighted_container, to_cnf


def create_model(instance):
    """People on a hospital waiting list for a kidney can donate to some of the
    others, as given by their compatibility lists. Maximize the number of people
    who receive a kidney: anyone who gives a kidney must receive one, and nobody
    receives more than one."""
    n_people = instance["num_people"]    # the number of people on the waiting list
    compatible = instance["compatible"]  # compatible[i]: the people, numbered from 1, that person i + 1 can donate to

    # transplants[i][j] is true when person i + 1 donates a kidney to person j + 1
    transplants = [[Bool(f"transplant_{i}_{j}") for j in range(n_people)] for i in range(n_people)]

    # allowed[i]: the indices of the people that person i + 1 can donate to
    allowed = [set(j - 1 for j in compatible[i]) for i in range(n_people)]
    # gives[i]: the number of kidneys person i + 1 donates
    gives = [sum(transplants[i][j] for j in range(n_people)) for i in range(n_people)]
    # receives[i]: the number of kidneys person i + 1 receives
    receives = [sum(transplants[k][i] for k in range(n_people)) for i in range(n_people)]

    # the conditions every set of transplants must meet
    constraints = []
    # Nobody donates a kidney to himself or herself.
    constraints += [~transplants[i][i] for i in range(n_people)]
    # A kidney goes only to a person on the donor's compatibility list.
    constraints += [~transplants[i][j] for i in range(n_people) for j in range(n_people) if j not in allowed[i]]
    # Nobody donates more than one kidney.
    constraints += [gives[i] <= 1 for i in range(n_people)]
    # Nobody receives more than one kidney.
    constraints += [receives[i] <= 1 for i in range(n_people)]
    # Anyone who donates a kidney receives one.
    constraints += [gives[i] - receives[i] <= 0 for i in range(n_people)]

    # The number of kidneys donated, which is the number of people who receive one.
    total = sum(gives)

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # maximise as soft clauses. The pool gives each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(total, And(constraints), to_cnf, formula, pool)

    return (formula, pool), {"transplants": transplants}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

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
    else:
        print("No solution")
