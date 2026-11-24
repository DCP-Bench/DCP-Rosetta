# jobs_puzzle: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobs_puzzle.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python jobs_puzzle.py

from pycsp3 import *


def create_model(instance):
    """Four people hold eight different jobs, each person exactly two: chef, guard, nurse, clerk,
    police officer, teacher, actor and boxer. Clues: 1. The nurse is not a teacher, police officer, or
    clerk. 2. The clerk is not the chef. 3. Person 0 is not the boxer. 4. Person 3 is not the teacher,
    police officer, or nurse. 5. Person 0, the chef, and the police officer went golfing together.
    Determine which person holds which two jobs."""
    n_people = 4
    jobs_each = 2  # each person holds exactly two jobs

    # The person (0 to 3) who holds each job
    chef = Var(dom=range(n_people))
    guard = Var(dom=range(n_people))
    nurse = Var(dom=range(n_people))
    clerk = Var(dom=range(n_people))
    police_officer = Var(dom=range(n_people))
    teacher = Var(dom=range(n_people))
    actor = Var(dom=range(n_people))
    boxer = Var(dom=range(n_people))

    satisfy(
        # Each person holds exactly two of the eight jobs.
        Cardinality(
            [chef, guard, nurse, clerk, police_officer, teacher, actor, boxer],
            occurrences={person: jobs_each for person in range(n_people)},
        ),
        # Clue 1: the nurse is not a teacher, police officer or clerk, so the nurse is not the person who holds any of them.
        [nurse != teacher, nurse != police_officer, nurse != clerk],
        # Clue 2: the clerk is not the chef.
        clerk != chef,
        # Clue 3: person 0 is not the boxer.
        boxer != 0,
        # Clue 4: person 3 is not the teacher, police officer or nurse.
        [teacher != 3, police_officer != 3, nurse != 3],
        # Clue 5, read as: person 0, the chef and the police officer are three different people (they went golfing together).
        [chef != 0, police_officer != 0, chef != police_officer],
    )

    return {
        "chef": chef,
        "guard": guard,
        "nurse": nurse,
        "clerk": clerk,
        "police_officer": police_officer,
        "teacher": teacher,
        "actor": actor,
        "boxer": boxer,
    }


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
