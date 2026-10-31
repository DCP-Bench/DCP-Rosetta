from hermax.model import Model


def build(instance):
    m = Model()

    # Extract instance data
    attributes = instance["attributes"]  # [20][5]: person attributes (languages/skills)
    required_crew = instance["required_crew"]  # [10][6]: required crew per flight

    num_flights = len(required_crew)
    num_people = len(attributes)

    # Decision variables: crew[f][p] = 1 if person p is assigned to flight f
    crew = m.bool_matrix("crew", num_flights, num_people)

    # Constraint 1: Each flight must have the required number of crew members
    # sum_p(crew[f][p]) == required_crew[f][0]
    for f in range(num_flights):
        m &= (sum(crew[f][p] for p in range(num_people)) == required_crew[f][0])

    # Constraint 2: Each flight must have enough crew with each required attribute
    # For each attribute a (1-5): sum_p(crew[f][p] * attributes[p][a-1]) >= required_crew[f][a]
    for f in range(num_flights):
        for a in range(1, 6):
            m &= (sum(crew[f][p] * attributes[p][a - 1] for p in range(num_people)) >= required_crew[f][a])

    # Constraint 3: Rest constraint - each person has two flights off after an attended flight
    # If crew[f][p] == 1, then crew[f+1][p] == 0 and crew[f+2][p] == 0
    for p in range(num_people):
        for f in range(num_flights - 1):
            m &= (crew[f][p] + crew[f + 1][p] <= 1)
        for f in range(num_flights - 2):
            m &= (crew[f][p] + crew[f + 2][p] <= 1)

    return m, {"crew": crew}
