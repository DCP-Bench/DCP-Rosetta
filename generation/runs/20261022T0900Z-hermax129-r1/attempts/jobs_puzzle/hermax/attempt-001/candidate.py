from hermax.model import Model

JOBS = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"]
PEOPLE = 4


def build(instance):
    m = Model()
    # Each job is held by one person, given as the person index 0-3.
    holder = {job: m.int(f"holder_{job}", 0, PEOPLE - 1) for job in JOBS}

    # Each person holds exactly two jobs.
    for p in range(PEOPLE):
        m &= (sum(holder[job] == p for job in JOBS) == 2)

    # Clue 1: the nurse is not a teacher, police officer, or clerk.
    for job in ("teacher", "police_officer", "clerk"):
        m &= (holder["nurse"] != holder[job])

    # Clue 2: the clerk is not the chef.
    m &= (holder["clerk"] != holder["chef"])

    # Clue 3: person 0 is not the boxer.
    m &= (holder["boxer"] != 0)

    # Clue 4: person 3 is not the teacher, police officer, or nurse.
    for job in ("teacher", "police_officer", "nurse"):
        m &= (holder[job] != 3)

    # Clue 5: person 0, the chef, and the police officer went golfing together,
    # so the chef and the police officer are two different people, both not
    # person 0.
    m &= (holder["chef"] != 0)
    m &= (holder["police_officer"] != 0)
    m &= (holder["chef"] != holder["police_officer"])

    outputs = {job: holder[job] for job in JOBS}
    return m, outputs
