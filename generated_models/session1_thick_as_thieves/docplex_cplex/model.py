# session1_thick_as_thieves: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_thick_as_thieves.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python session1_thick_as_thieves.py

from docplex.mp.model import Model


def create_model(instance):
    """Six suspects were interviewed about a robbery. The getaway car held at most two, so at least
    four are innocent. The innocent tell the truth and the guilty lie. From their statements,
    find who is guilty."""
    model = Model("thick_as_thieves")
    names = ["artie", "bill", "crackitt", "dodgy", "edgy", "fingers"]
    # guilty[x] is 1 when suspect x is guilty, and 0 when innocent
    guilty = {x: model.binary_var(name=x) for x in names}
    artie, bill, crackitt, dodgy, edgy, fingers = (guilty[x] for x in names)

    # The getaway car held at most two, so at most two are guilty.
    model.add_constraint(model.sum(guilty.values()) <= 2)

    # A suspect is guilty exactly when his statement is false.
    # Artie: "It wasn't me." False exactly when Artie is guilty, so it holds whatever Artie is.
    # Bill: "Crackitt was in it." Bill is guilty exactly when Crackitt is not.
    model.add_constraint(bill + crackitt == 1)
    # Crackitt: "No I wasn't." Like Artie's, it holds whatever Crackitt is.
    # Dodgy: "If Crackitt did it, Bill did it with him." False exactly when Crackitt is
    # guilty and Bill is not: dodgy == crackitt and not bill.
    model.add_constraint(dodgy <= crackitt)
    model.add_constraint(dodgy <= 1 - bill)
    model.add_constraint(dodgy >= crackitt - bill)
    # Edgy: "Nobody did it alone" (more than one is guilty). False exactly when at most one
    # is guilty.
    model.add_equivalence(edgy, model.sum(guilty.values()) <= 1)
    # Fingers: "It was Artie and Dodgy together." False exactly when not both are guilty:
    # fingers == not (artie and dodgy).
    model.add_constraint(fingers + artie >= 1)
    model.add_constraint(fingers + dodgy >= 1)
    model.add_constraint(fingers + artie + dodgy <= 2)

    return model, dict(guilty)


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
