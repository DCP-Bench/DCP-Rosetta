# jobs_puzzle: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobs_puzzle.html
# Run it (after `pip install hermax`) with:
#   python jobs_puzzle.py

from hermax.model import Model

# Four people (numbered 0 to 3) hold eight different jobs, two jobs each.
# Five clues fix which person holds which job. The statement fixes all the
# data, so the instance carries no fields and is not read.

# The eight jobs, in the order the statement lists them.
JOBS = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"]
PEOPLE = 4  # the four people, numbered 0 to 3


def create_model(instance):
    """Four people hold eight jobs, two each. Find the person (0-3) holding each job,
    so that the five clues hold: the nurse is not a teacher, police officer or clerk;
    the clerk is not the chef; person 0 is not the boxer; person 3 is not the teacher,
    police officer or nurse; and person 0, the chef and the police officer went golfing
    together, so those three are three different people."""
    m = Model()

    # holder[job] is the person (0 to 3) who holds that job; each job has exactly one holder.
    holder = {job: m.int(f"holder_{job}", 0, PEOPLE - 1) for job in JOBS}

    # Each person holds exactly two jobs.
    for person in range(PEOPLE):
        m &= (sum(holder[job] == person for job in JOBS) == 2)

    # Clue 1: the nurse is not a teacher, police officer or clerk.
    for job in ("teacher", "police_officer", "clerk"):
        m &= (holder["nurse"] != holder[job])

    # Clue 2: the clerk is not the chef.
    m &= (holder["clerk"] != holder["chef"])

    # Clue 3: person 0 is not the boxer.
    m &= (holder["boxer"] != 0)

    # Clue 4: person 3 is not the teacher, police officer or nurse.
    for job in ("teacher", "police_officer", "nurse"):
        m &= (holder[job] != 3)

    # Clue 5: person 0, the chef and the police officer went golfing together, so the
    # chef and the police officer are two different people, neither of them person 0.
    m &= (holder["chef"] != 0)
    m &= (holder["police_officer"] != 0)
    m &= (holder["chef"] != holder["police_officer"])

    # The output: for each job, the person (0 to 3) holding it.
    outputs = {job: holder[job] for job in JOBS}
    return m, outputs


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
