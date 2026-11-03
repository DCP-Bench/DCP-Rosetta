# jobs_puzzle: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobs_puzzle.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python jobs_puzzle.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Four people hold eight different jobs, two jobs each: chef, guard, nurse, clerk,
    police officer, teacher, actor and boxer. Five clues rule out some assignments.
    Find which person holds which job."""
    # The puzzle gives its people and jobs, so the instance is not read.
    people = range(4)  # people 0 to 3
    jobs = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"]

    # holds[j][p] is true when person p holds job j
    holds = {j: {p: Bool(f"holds_{j}_{p}") for p in people} for j in jobs}

    # Each job is held by exactly one person.
    constraints = [sum(holds[j].values()) == 1 for j in jobs]

    # Each person holds exactly two jobs.
    constraints += [sum(holds[j][p] for j in jobs) == 2 for p in people]

    # Clue 1: the nurse is not a teacher, a police officer or a clerk.
    for other in ["teacher", "police_officer", "clerk"]:
        for p in people:
            constraints.append(~(holds["nurse"][p] & holds[other][p]))

    # Clue 2: the clerk is not the chef.
    for p in people:
        constraints.append(~(holds["clerk"][p] & holds["chef"][p]))

    # Clue 3: person 0 is not the boxer.
    constraints.append(~holds["boxer"][0])

    # Clue 4: person 3 is not the teacher, the police officer or the nurse.
    for j in ["teacher", "police_officer", "nurse"]:
        constraints.append(~holds[j][3])

    # Clue 5: person 0, the chef and the police officer went golfing together, so they
    # are three different people.
    constraints.append(~holds["chef"][0])
    constraints.append(~holds["police_officer"][0])
    for p in people:
        constraints.append(~(holds["chef"][p] & holds["police_officer"][p]))

    # The person index holding each job.
    outputs = {j: sum(p * holds[j][p] for p in people) for j in jobs}

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), outputs


if __name__ == "__main__":
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    (formula, pool), outputs = create_model({})

    solver = SatSolver.from_name("Cadical300")
    # copy the formula into the solver
    solver.add_clauses(formula.clauses())

    if solver.solve():
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
