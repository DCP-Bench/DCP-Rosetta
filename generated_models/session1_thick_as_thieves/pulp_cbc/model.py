# session1_thick_as_thieves: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_thick_as_thieves.html
# Run it (after `pip install pulp numpy`) with:
#   python session1_thick_as_thieves.py

import pulp


def create_model(instance):
    """Six suspects in a robbery, at most two of them guilty. The innocent
    tell the truth and the guilty lie. Who is guilty?"""
    problem = pulp.LpProblem("thick_as_thieves", pulp.LpMinimize)

    # 1 when the suspect is guilty, and 0 when innocent
    artie = pulp.LpVariable("artie", cat="Binary")
    bill = pulp.LpVariable("bill", cat="Binary")
    crackitt = pulp.LpVariable("crackitt", cat="Binary")
    dodgy = pulp.LpVariable("dodgy", cat="Binary")
    edgy = pulp.LpVariable("edgy", cat="Binary")
    fingers = pulp.LpVariable("fingers", cat="Binary")
    suspects = [artie, bill, crackitt, dodgy, edgy, fingers]
    count = pulp.lpSum(suspects)  # how many suspects are guilty

    # The getaway car held only two, so at most two of them are guilty.
    problem += count <= 2

    # Bill says Crackitt was in it, so Bill is guilty exactly when Crackitt is not.
    problem += bill == 1 - crackitt

    # Dodgy is guilty exactly when Crackitt is guilty and Bill is not.
    problem += dodgy <= crackitt
    problem += dodgy <= 1 - bill
    problem += dodgy >= crackitt - bill

    # Edgy is guilty exactly when at most one suspect is guilty.
    problem += count <= 1 + (len(suspects) - 1) * (1 - edgy)
    problem += count >= 2 * (1 - edgy)

    # both is 1 when Artie and Dodgy are both guilty.
    both = pulp.LpVariable("artie_and_dodgy", cat="Binary")
    problem += both <= artie
    problem += both <= dodgy
    problem += both >= artie + dodgy - 1

    # Fingers is guilty exactly when it is not true that Artie and Dodgy did it together.
    problem += fingers == 1 - both

    return problem, {
        "artie": artie, "bill": bill, "crackitt": crackitt,
        "dodgy": dodgy, "edgy": edgy, "fingers": fingers,
    }


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
