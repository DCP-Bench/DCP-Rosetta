# session3_exodus: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_exodus.html
# Run it (after `pip install pulp numpy`) with:
#   python session3_exodus.py

import pulp


def create_model(instance):
    """Five children at Hebrew school (Bernice, Carl, Debby, Sammy and Ted) each
    tell one part of the Exodus story: the burning bush, the captivity, Moses's
    youth, the Passover or the Ten Commandments. Each child is a different age
    (3, 5, 7, 8 or 10), and each family came to America from a different country
    (Ethiopia, Kazakhstan, Lithuania, Morocco or Yemen). Find the age, country and
    story of each child from the clues."""

    # Child numbers 1 to 5. Items of different categories with the same number
    # belong to the same child.
    slots = range(1, 6)
    # The items of each category: the children, their ages, their countries and their stories.
    categories = {
        "ages": ["age3", "age5", "age7", "age8", "age10"],
        "children": ["bernice", "carl", "debby", "sammy", "ted"],
        "countries": ["ethiopia", "kazakhstan", "lithuania", "morocco", "yemen"],
        "stories": ["burning_bush", "captivity", "moses_youth", "passover", "ten_commandments"],
    }
    # The number of years each age item stands for.
    age_value = {"age3": 3, "age5": 5, "age7": 7, "age8": 8, "age10": 10}

    problem = pulp.LpProblem("exodus", pulp.LpMinimize)

    # in_slot[e][s] is 1 when item e has child number s, and 0 when not
    in_slot = {e: {s: pulp.LpVariable(f"slot_{e}_{s}", cat="Binary") for s in slots}
               for items in categories.values() for e in items}

    # The age of the child who has item e. same_age[a] is 1 when age a has the same
    # child number as e, and exactly one age does.
    def age_of(e):
        same_age = {a: pulp.LpVariable(f"age_{e}_{a}", cat="Binary") for a in categories["ages"]}
        for a, var in same_age.items():
            for s in slots:
                problem.addConstraint(var >= in_slot[e][s] + in_slot[a][s] - 1)
        problem.addConstraint(pulp.lpSum(same_age.values()) == 1)
        return pulp.lpSum(age_value[a] * var for a, var in same_age.items())

    # Each item has exactly one child number, and within a category each child
    # number is used by one item only.
    for items in categories.values():
        for e in items:
            problem += pulp.lpSum(in_slot[e].values()) == 1
        for s in slots:
            problem += pulp.lpSum(in_slot[e][s] for e in items) == 1

    # 1. Debby's family is from Lithuania.
    for s in slots:
        problem += in_slot["debby"][s] == in_slot["lithuania"][s]

    # 2. The child who told the story of the Passover is two years older than Bernice.
    problem += age_of("passover") == age_of("bernice") + 2

    # 3. The child from the Yemeni family is younger than the child from the Ethiopian family.
    problem += age_of("yemen") + 1 <= age_of("ethiopia")

    # 4. The child from the Moroccan family is three years older than Ted.
    problem += age_of("morocco") == age_of("ted") + 3

    # 5. Sammy is three years older than the child who told the story of Moses's youth.
    problem += age_of("sammy") == age_of("moses_youth") + 3

    # Each item's child number, by category. Items with the same number belong to the same child.
    outputs = {}
    for category, items in categories.items():
        outputs[category] = [pulp.lpSum(s * in_slot[e][s] for s in slots) for e in items]

    return problem, outputs


if __name__ == "__main__":
    import numpy as np

    problem, outputs = create_model({})
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
