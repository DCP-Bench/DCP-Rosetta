# crew: a CPLEX (Python) model from DCP Rosetta.
# Download the `crew.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crew.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python crew.py crew.json

from docplex.mp.model import Model


def create_model(instance):
    """Assign flight attendants to flights. Each flight needs exactly a certain number of cabin crew,
    with at least the required number of stewards, hostesses and speakers of French, Spanish and
    German (one person can count towards several). Every cabin crew member has at least two
    flights off after an attended flight, so nobody attends more than one of any three
    consecutive flights."""
    attributes = instance["attributes"]        # attributes[p][k]: 1 if person p has attribute k, else 0
    required_crew = instance["required_crew"]  # required_crew[f]: the cabin crew of flight f, then the least number needed of each attribute
    persons = range(len(attributes))
    n_flights = len(required_crew)
    flights = range(n_flights)
    # the attributes k are: 0 steward, 1 hostess, 2 speaks French, 3 speaks Spanish, 4 speaks German
    kinds = range(len(attributes[0]))

    model = Model("crew")

    # crew[f, p] is 1 when person p is assigned to flight f, and 0 when not
    crew = model.binary_var_matrix(flights, persons, name="crew")

    for f in flights:
        crew_size, *least = required_crew[f]  # the cabin crew of flight f, and the least number needed of each attribute
        # The flight has exactly the cabin crew it needs.
        model.add_constraint(model.sum(crew[f, p] for p in persons) == crew_size, ctname=f"size_{f}")
        # It has at least the required number of stewards, hostesses and speakers of each language.
        for k in kinds:
            model.add_constraint(model.sum(attributes[p][k] * crew[f, p] for p in persons)
                                 >= least[k], ctname=f"attribute_{f}_{k}")

    # Nobody attends more than one of any three consecutive flights: two flights off after each
    # flight attended.
    model.add_constraints(crew[f, p] + crew[f + 1, p] + crew[f + 2, p] <= 1
                          for f in range(n_flights - 2) for p in persons)

    return model, {"crew": [[crew[f, p] for p in persons] for f in flights]}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
