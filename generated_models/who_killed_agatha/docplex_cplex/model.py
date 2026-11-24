# who_killed_agatha: a CPLEX (Python) model from DCP Rosetta.
# Download the `who_killed_agatha.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/who_killed_agatha.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python who_killed_agatha.py who_killed_agatha.json

from docplex.mp.model import Model


def create_model(instance):
    """Who killed Agatha: Agatha, the butler and Charles live in Dreadsbury Mansion and one of
    them killed Agatha. From who hates whom and who is richer, find the killer."""
    names = instance["names"]  # names[i]: the name of resident i
    n = len(names)
    people = range(n)
    agatha, butler, charles = 0, 1, 2  # the residents, in the order the statement lists them
    victim = agatha

    model = Model("who_killed_agatha")

    # hates[i, j] is 1 when resident i hates resident j
    hates = {(i, j): model.binary_var(name=f"hates_{i}_{j}") for i in people for j in people}
    # richer[i, j] is 1 when resident i is richer than resident j
    richer = {(i, j): model.binary_var(name=f"richer_{i}_{j}") for i in people for j in people}

    # is_killer[i] is 1 when resident i is the killer; exactly one of them.
    is_killer = [model.binary_var(name=f"killer_is_{i}") for i in people]
    model.add_constraint(model.sum(is_killer) == 1)

    # A killer always hates, and is no richer than, his victim.
    model.add_constraints(is_killer[i] <= hates[i, victim] for i in people)
    model.add_constraints(is_killer[i] <= 1 - richer[i, victim] for i in people)

    # Richer is a strict comparison: no one is richer than himself, and of two different people
    # exactly one is richer (background assumed by the puzzle, not one of its clues).
    for i in people:
        model.add_constraint(richer[i, i] == 0)
        for j in people:
            if i < j:
                model.add_constraint(richer[i, j] == 1 - richer[j, i])

    # Charles hates no one that Agatha hates.
    model.add_constraints(hates[agatha, i] + hates[charles, i] <= 1 for i in people)

    # Agatha hates everybody except the butler.
    model.add_constraint(hates[agatha, agatha] == 1)
    model.add_constraint(hates[agatha, charles] == 1)
    model.add_constraint(hates[agatha, butler] == 0)

    # The butler hates everyone not richer than Aunt Agatha.
    model.add_constraints(1 - richer[i, agatha] <= hates[butler, i] for i in people)

    # The butler hates everyone whom Agatha hates.
    model.add_constraints(hates[agatha, i] <= hates[butler, i] for i in people)

    # No one hates everyone.
    model.add_constraints(model.sum(hates[i, j] for j in people) <= n - 1 for i in people)

    # The killer is reported as the 0-based index of the resident who killed Agatha.
    killer = model.sum(i * is_killer[i] for i in people)

    return model, {"killer": killer}


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
