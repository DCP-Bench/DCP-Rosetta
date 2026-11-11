# session3_exodus: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_exodus.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python session3_exodus.py

from docplex.mp.model import Model


def create_model(instance):
    """Five children at Hebrew school each present a different part of the Exodus story, are of a
    different age, and come from a family from a different country. From five clues, find the age,
    the country and the part of the story of each child."""
    # Items that get the same slot belong together: they are the same child, age, country and story.
    slots = range(1, 6)
    ages = {"age3": 3, "age5": 5, "age7": 7, "age8": 8, "age10": 10}  # the age in years of each age item
    groups = {
        "ages": list(ages),
        "children": ["bernice", "carl", "debby", "sammy", "ted"],
        "countries": ["ethiopia", "kazakhstan", "lithuania", "morocco", "yemen"],
        "stories": ["burning_bush", "captivity", "moses_youth", "passover", "ten_commandments"],
    }

    model = Model("exodus")

    # at[e, s] is 1 when item e has slot s. Within a group every item has one slot and no
    # two items share one (all different).
    at = {}
    for items in groups.values():
        for e in items:
            for s in slots:
                at[e, s] = model.binary_var(name=f"{e}_at_{s}")
            model.add_constraint(model.sum(at[e, s] for s in slots) == 1)
        for s in slots:
            model.add_constraint(model.sum(at[e, s] for e in items) == 1)

    # age_of(e) is the age in years of item e (a child, country or story): the age item that
    # shares its slot. has_age[a] is 1 when item e shares its slot with age item a: if e and a
    # are both at slot s, has_age[a] is forced to 1, and exactly one is chosen.
    def age_of(e):
        has_age = {a: model.binary_var(name=f"{e}_has_{a}") for a in ages}
        for a in ages:
            for s in slots:
                model.add_constraint(has_age[a] >= at[e, s] + at[a, s] - 1)
        model.add_constraint(model.sum(has_age.values()) == 1)
        return model.sum(ages[a] * has_age[a] for a in ages)

    # 1. Debby's family is from Lithuania.
    model.add_constraints(at["debby", s] == at["lithuania", s] for s in slots)
    # 2. The child who told the Passover story is two years older than Bernice.
    model.add_constraint(age_of("passover") == age_of("bernice") + 2)
    # 3. The child from Yemen is younger than the child from Ethiopia.
    model.add_constraint(age_of("yemen") <= age_of("ethiopia") - 1)
    # 4. The child from Morocco is three years older than Ted.
    model.add_constraint(age_of("morocco") == age_of("ted") + 3)
    # 5. Sammy is three years older than the child who told of Moses's youth.
    model.add_constraint(age_of("sammy") == age_of("moses_youth") + 3)

    # Each output lists the slot of every item of a group, in the statement's order.
    outputs = {name: [model.sum(s * at[e, s] for s in slots) for e in items]
               for name, items in groups.items()}
    return model, outputs


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
