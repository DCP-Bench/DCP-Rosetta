# crew: a PyCSP3 model from DCP Rosetta.
# Download the `crew.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crew.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python crew.py crew.json

from pycsp3 import *


def create_model(instance):
    """Assign flight attendants to flights. Each flight needs exactly a given number
    of cabin crew, and at least a given number of people speaking each of the
    required languages or skills; one person can count towards several of them.
    Every cabin crew member has at least two flights off after an attended flight,
    so nobody attends more than one of any three consecutive flights."""
    attributes = instance["attributes"]        # attributes[p]: person p as 0/1 values for the skills, in the order of skills
    required_crew = instance["required_crew"]  # required_crew[f]: flight f's crew total, then the number needed of each skill
    skills = ["steward", "hostess", "French", "Spanish", "German"]
    n_skills = len(skills)
    n_people = len(attributes)     # one row per person
    n_flights = len(required_crew)  # one row per flight
    window = 3  # any three consecutive flights: the two flights off after an attended flight
    total_column = 0       # required_crew[f][0]: the number of cabin crew on flight f
    first_skill_column = 1  # required_crew[f][1 + k]: the number needed of skill k on flight f

    # crew[f][p] = 1 when person p is assigned to flight f; 0 otherwise.
    crew = VarArray(size=[n_flights, n_people], dom={0, 1})

    satisfy(
        # Each flight has exactly the required number of cabin crew.
        [Sum(crew[f]) == required_crew[f][total_column] for f in range(n_flights)],
        # Each flight has at least the required number of people with each skill.
        [Sum(crew[f][p] for p in range(n_people) if attributes[p][k] == 1) >= required_crew[f][first_skill_column + k]
         for k in range(n_skills) for f in range(n_flights)],
        # Nobody attends more than one flight of any three consecutive flights.
        [Sum(crew[f:f + window, p]) <= 1 for p in range(n_people) for f in range(n_flights - window + 1)],
    )

    return {"crew": crew}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        print("crew", "=")
        for row in outputs["crew"]:
            print(values(row))
    else:
        print("No solution:", status())
