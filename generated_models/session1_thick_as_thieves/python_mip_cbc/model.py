# session1_thick_as_thieves: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_thick_as_thieves.html
# Run it (after `pip install mip numpy`) with:
#   python session1_thick_as_thieves.py

import mip


def create_model(instance):
    """Six suspects make statements about a robbery. The getaway car barely held
    two, so at most two of them are guilty. The innocent tell the truth and the
    guilty lie. Who is guilty?"""
    model = mip.Model(solver_name="CBC")

    # Each variable is 1 when that suspect is guilty, and 0 when innocent.
    artie = model.add_var("artie", var_type=mip.BINARY)
    bill = model.add_var("bill", var_type=mip.BINARY)
    crackitt = model.add_var("crackitt", var_type=mip.BINARY)
    dodgy = model.add_var("dodgy", var_type=mip.BINARY)
    edgy = model.add_var("edgy", var_type=mip.BINARY)
    fingers = model.add_var("fingers", var_type=mip.BINARY)
    suspects = [artie, bill, crackitt, dodgy, edgy, fingers]

    # The getaway car held two, so the number of guilty suspects is zero, one or two.
    none_guilty = model.add_var("count_zero", var_type=mip.BINARY)
    one_guilty = model.add_var("count_one", var_type=mip.BINARY)
    two_guilty = model.add_var("count_two", var_type=mip.BINARY)
    model.add_constr(none_guilty + one_guilty + two_guilty == 1)
    # The number of guilty suspects is the count that holds.
    model.add_constr(mip.xsum(suspects) == one_guilty + 2 * two_guilty)

    # Artie's and Crackitt's statements are about their own guilt. Each is false
    # exactly when that suspect is guilty, so they add no rule.

    # Bill's statement is that Crackitt is guilty. Bill is guilty exactly when it is false.
    model.add_constr(bill + crackitt == 1)

    # Dodgy is guilty exactly when his statement is false: Crackitt is guilty and Bill is not.
    model.add_constr(dodgy >= crackitt - bill)
    model.add_constr(dodgy <= crackitt)
    model.add_constr(dodgy + bill <= 1)

    # Edgy is guilty exactly when his statement is false: exactly one suspect is guilty.
    model.add_constr(edgy == one_guilty)

    # artie_and_dodgy is 1 exactly when Artie and Dodgy are both guilty.
    artie_and_dodgy = model.add_var("artie_and_dodgy", var_type=mip.BINARY)
    model.add_constr(artie_and_dodgy <= artie)
    model.add_constr(artie_and_dodgy <= dodgy)
    model.add_constr(artie_and_dodgy >= artie + dodgy - 1)
    # Fingers is guilty exactly when his statement is false: Artie and Dodgy are not both guilty.
    model.add_constr(fingers + artie_and_dodgy == 1)

    return model, {
        "artie": artie,
        "bill": bill,
        "crackitt": crackitt,
        "dodgy": dodgy,
        "edgy": edgy,
        "fingers": fingers,
    }


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
