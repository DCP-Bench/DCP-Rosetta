# jobs_puzzle: a FOX model for GroundFOX from DCP Rosetta.
#
# Four people hold eight different jobs. Each person holds exactly two jobs. The jobs are:
# chef, guard, nurse, clerk, police officer, teacher, actor, and boxer.
#
# Clues: 1. The nurse is not a teacher, police officer, or clerk. 2. The clerk is not the
# chef. 3. Person 0 is not the boxer. 4. Person 3 is not the teacher, police officer, or
# nurse. 5. Person 0, the chef, and the police officer went golfing together.
#
# Determine which person holds which two jobs.
#
# Print the person index, 0-3, assigned to each job (chef, guard, nurse, clerk,
# police_officer, teacher, actor, boxer).
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobs_puzzle.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py jobs_puzzle.json --check

JOBS = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"]

_lines =["invocabulary { Per/1 Zero/1 Three/1 }",
          "outvocabulary { " + " ".join(j + "/1" for j in JOBS) + " }",
          "theory {"]
for _j in JOBS:
    # every job is held by exactly one person
    _lines.append("    ? p [Per(p)] : %s(p)." % _j)
    _lines.append("    ! p [Per(p)] : ! q [Per(q) & p ~= q] : ~%s(p) | ~%s(q)." % (_j, _j))
# every person holds at most two jobs (8 jobs, 4 people: exactly two each)
for _a in range(len(JOBS)):
    for _b in range(_a + 1, len(JOBS)):
        for _c in range(_b + 1, len(JOBS)):
            _lines.append("    ! p [Per(p)] : ~%s(p) | ~%s(p) | ~%s(p)." % (JOBS[_a], JOBS[_b], JOBS[_c]))
_lines += [
    # 1. the nurse is not a teacher, police officer or clerk
    "    ! p [Per(p)] : ~nurse(p) | ~teacher(p).",
    "    ! p [Per(p)] : ~nurse(p) | ~police_officer(p).",
    "    ! p [Per(p)] : ~nurse(p) | ~clerk(p).",
    # 2. the clerk is not the chef
    "    ! p [Per(p)] : ~clerk(p) | ~chef(p).",
    # 3. person 0 is not the boxer
    "    ! p [Zero(p)] : ~boxer(p).",
    # 4. person 3 is not the teacher, police officer or nurse
    "    ! p [Three(p)] : ~teacher(p).",
    "    ! p [Three(p)] : ~police_officer(p).",
    "    ! p [Three(p)] : ~nurse(p).",
    # 5. person 0, the chef and the police officer are three different people
    "    ! p [Zero(p)] : ~chef(p).",
    "    ! p [Zero(p)] : ~police_officer(p).",
    "    ! p [Per(p)] : ~chef(p) | ~police_officer(p).",
    "}",
]
FOX = "\n".join(_lines) + "\n"


def structure(instance):
    return {"Per": range(4), "Zero": [0], "Three": [3]}
