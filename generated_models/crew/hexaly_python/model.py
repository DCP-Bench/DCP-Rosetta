"""Crew scheduling: staff each flight with the required cabin crew and languages, with two flights off after each one."""
import hexaly.optimizer as hx


def build(instance):
    attributes = instance["attributes"]  # attributes[p][a] = 1 if person p has attribute a
    required = instance["required_crew"]  # required[f] = [crew size, then the minimum per attribute]
    people, flights = len(attributes), len(required)
    n_attr = len(attributes[0])
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # crew[f][p] = 1 if person p works on flight f
    crew = [[model.bool() for _ in range(people)] for _ in range(flights)]

    for f in range(flights):
        # The flight gets exactly the crew size it needs
        model.constraint(model.sum(crew[f]) == required[f][0])
        # and at least the required number of people with each attribute (role or language)
        for a in range(n_attr):
            model.constraint(model.sum(crew[f][p] for p in range(people) if attributes[p][a]) >= required[f][a + 1])
    # After attending a flight, a person has the next two flights off
    for p in range(people):
        for f in range(flights):
            model.constraint(model.sum(crew[g][p] for g in range(f, min(flights, f + 3))) <= 1)

    return optimizer, {"crew": crew}
