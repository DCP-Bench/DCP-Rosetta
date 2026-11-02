"""Jobs puzzle: four people hold eight jobs, exactly two each; which person holds which jobs?"""
import hexaly.optimizer as hx

JOBS = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"]


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # holder[job] is the person (0..3) who holds the job
    holder = {job: model.int(0, 3) for job in JOBS}
    # Each person holds exactly two jobs
    for person in range(4):
        model.constraint(model.sum(holder[job] == person for job in JOBS) == 2)

    # 1. The nurse is not a teacher, police officer or clerk
    for job in ("teacher", "police_officer", "clerk"):
        model.constraint(holder["nurse"] != holder[job])
    # 2. The clerk is not the chef
    model.constraint(holder["clerk"] != holder["chef"])
    # 3. Person 0 is not the boxer
    model.constraint(holder["boxer"] != 0)
    # 4. Person 3 is not the teacher, police officer or nurse
    for job in ("teacher", "police_officer", "nurse"):
        model.constraint(holder[job] != 3)
    # 5. Person 0, the chef and the police officer are three different people
    model.constraint(holder["chef"] != 0)
    model.constraint(holder["police_officer"] != 0)
    model.constraint(holder["chef"] != holder["police_officer"])

    return optimizer, holder
