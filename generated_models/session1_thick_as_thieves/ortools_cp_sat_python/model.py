# session1_thick_as_thieves: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_thick_as_thieves.html
# Run it (after `pip install ortools`) with:
#   python session1_thick_as_thieves.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Six suspects make statements about a robbery. Find out who is guilty."""
    model = cp_model.CpModel()

    def conjunction(conditions, name):
        """A new variable that is true exactly when every one of the conditions holds."""
        holds = model.new_bool_var(name)
        model.add_bool_and(conditions).only_enforce_if(holds)
        model.add_bool_or([~c for c in conditions]).only_enforce_if(~holds)
        return holds

    def guilty_iff_claim_false(speaker, claim):
        """A suspect is guilty exactly when their statement is false."""
        model.add(speaker + claim == 1)

    # Each variable is true when that suspect is guilty.
    artie = model.new_bool_var("artie")
    bill = model.new_bool_var("bill")
    crackitt = model.new_bool_var("crackitt")
    dodgy = model.new_bool_var("dodgy")
    edgy = model.new_bool_var("edgy")
    fingers = model.new_bool_var("fingers")

    # All six suspects.
    suspects = [artie, bill, crackitt, dodgy, edgy, fingers]

    # The getaway car barely held two, so at most two suspects are guilty.
    model.add(sum(suspects) <= 2)

    # Artie: "It wasn't me."
    guilty_iff_claim_false(artie, ~artie)
    # Bill: "Crackitt was in it up to his neck."
    guilty_iff_claim_false(bill, crackitt)
    # Crackitt: "No I wasn't."
    guilty_iff_claim_false(crackitt, ~crackitt)
    # Dodgy: "If Crackitt did it, Bill did it with him." The statement is false
    # exactly when Crackitt is guilty and Bill is not.
    implication_fails = conjunction([crackitt, ~bill], "dodgy_claim_fails")
    guilty_iff_claim_false(dodgy, ~implication_fails)
    # Edgy: "Nobody did it alone." The statement is true when more than one is guilty.
    more_than_one = model.new_bool_var("more_than_one")
    model.add(sum(suspects) > 1).only_enforce_if(more_than_one)
    model.add(sum(suspects) <= 1).only_enforce_if(~more_than_one)
    guilty_iff_claim_false(edgy, more_than_one)
    # Fingers: "It was Artie and Dodgy together."
    artie_and_dodgy = conjunction([artie, dodgy], "artie_and_dodgy")
    guilty_iff_claim_false(fingers, artie_and_dodgy)

    return model, {
        "artie": artie, "bill": bill, "crackitt": crackitt,
        "dodgy": dodgy, "edgy": edgy, "fingers": fingers,
    }


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
