# session3_people_in_a_room: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_people_in_a_room.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python session3_people_in_a_room.py

from docplex.mp.model import Model


def create_model(instance):
    """People in a room: 13 people, 4 of them male, enter a room one at a time; order them so
    that the ratio of females to males in the room is never above 7/3."""
    total_people = 13  # the number of people entering the room
    num_males = 4      # how many of them are male
    num_females = total_people - num_males

    model = Model("people_in_a_room")

    # sequence[i] is 1 when the i-th person to enter is female, 0 when male.
    sequence = [model.binary_var(name=f"female_{i}") for i in range(total_people)]

    # Exactly num_females of them are female.
    model.add_constraint(model.sum(sequence) == num_females)

    # Whenever i people have entered, the ratio of females to males in the room is at most 7/3:
    # 3 * females <= 7 * males, with males = i - females.
    for i in range(1, total_people + 1):
        females = model.sum(sequence[:i])
        model.add_constraint(3 * females <= 7 * (i - females))

    return model, {"sequence": sequence}


if __name__ == "__main__":
    model, outputs = create_model({})
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
