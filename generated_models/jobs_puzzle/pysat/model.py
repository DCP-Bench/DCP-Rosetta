# jobs_puzzle: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobs_puzzle.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python jobs_puzzle.py

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine

# The eight jobs, each held by one person.
JOBS = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"]


def create_model(instance):
    """Four people hold eight different jobs, two each. Five clues say who is not which,
    and the model finds the person who holds each job."""
    n_people = 4  # the people, numbered 0 to 3

    pool = IDPool()

    # job[name]: the person (0 to 3) who holds that job
    job = {name: Integer(name, 0, n_people - 1, vpool=pool) for name in JOBS}
    engine = IntegerEngine(vars=list(job.values()), vpool=pool)
    cnf = engine.clausify()

    def apart(first, second):
        # The two jobs are held by different people.
        for person in range(n_people):
            cnf.append([-job[first].equals(person), -job[second].equals(person)])

    def not_held_by(name, person):
        cnf.append([-job[name].equals(person)])

    # Each person holds exactly two of the jobs.
    for person in range(n_people):
        cnf.extend(CardEnc.equals(lits=[job[name].equals(person) for name in JOBS], bound=2,
                                  vpool=pool, encoding=EncType.seqcounter).clauses)

    # The nurse is not the teacher, the police officer or the clerk.
    apart("nurse", "teacher")
    apart("nurse", "police_officer")
    apart("nurse", "clerk")

    # The clerk is not the chef.
    apart("clerk", "chef")

    # Person 0 is not the boxer.
    not_held_by("boxer", 0)

    # Person 3 is not the teacher, the police officer or the nurse.
    not_held_by("teacher", 3)
    not_held_by("police_officer", 3)
    not_held_by("nurse", 3)

    # Person 0, the chef and the police officer went golfing together, so the three of them
    # are different people.
    not_held_by("chef", 0)
    not_held_by("police_officer", 0)
    apart("chef", "police_officer")

    return cnf, job


if __name__ == "__main__":
    import numpy as np
    from pysat.solvers import Solver

    formula, outputs = create_model({})

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
