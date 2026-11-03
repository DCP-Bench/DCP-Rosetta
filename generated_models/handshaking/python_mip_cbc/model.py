# handshaking: a Python-MIP (Python) model from DCP Rosetta.
# Download the `handshaking.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/handshaking.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python handshaking.py handshaking.json

import mip


def create_model(instance):
    """Hilary and Jocelyn are married and invite some couples for dinner. Everybody
    shakes hands with some of the others, but nobody shakes hands with themselves or
    with their spouse. Jocelyn asks how many hands each person has shaken, and all the
    answers are different. How many hands has Hilary shaken?"""
    num_couples = instance["num_couples"]  # the number of invited couples
    total_couples = num_couples + 1        # the invited couples and Hilary and Jocelyn
    persons = 2 * total_couples            # everyone at dinner
    # Nobody shakes hands with themselves or with their spouse, so the most hands a person
    # can shake is persons - 2.
    max_hands = persons - 2

    # Person 2k and person 2k+1 are spouses. Person 0 is Hilary and person 1 is Jocelyn.
    def spouse(i):
        return i + 1 if i % 2 == 0 else i - 1

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # shake[i, j] is 1 when persons i and j shake hands. Only pairs of different people
    # who are not spouses get a variable.
    shake = {}
    for i in range(persons):
        for j in range(i + 1, persons):
            if j != spouse(i):
                shake[i, j] = model.add_var(f"shake_{i}_{j}", var_type=mip.BINARY)

    # The handshake between persons i and j, in either order.
    def handshake(i, j):
        return shake[min(i, j), max(i, j)]

    # hands[i] is the number of hands person i has shaken.
    hands = []
    # Each person's hands count is the number of handshakes that person takes part in.
    for i in range(persons):
        h = model.add_var(f"hands_{i}", lb=0, ub=max_hands, var_type=mip.INTEGER)
        model.add_constr(h == mip.xsum(handshake(i, j) for j in range(persons) if j != i and j != spouse(i)))
        hands.append(h)

    # Jocelyn asks everyone except herself.
    answerers = [i for i in range(persons) if i != 1]
    # pick[i, v] is 1 when person i gives the answer v.
    pick = {}
    # Each answerer gives one answer, and that answer is the person's hands count.
    for i in answerers:
        for v in range(max_hands + 1):
            pick[i, v] = model.add_var(f"pick_{i}_{v}", var_type=mip.BINARY)
        model.add_constr(mip.xsum(pick[i, v] for v in range(max_hands + 1)) == 1)
        model.add_constr(hands[i] == mip.xsum(v * pick[i, v] for v in range(max_hands + 1)))
    # All the answers are different. There are as many answerers as values from 0 to
    # max_hands, so each value is given exactly once.
    for v in range(max_hands + 1):
        model.add_constr(mip.xsum(pick[i, v] for i in answerers) == 1)

    # In each invited couple, the two hands counts add up to max_hands. The answers cover
    # 0 to max_hands, so a person with k hands has a spouse with max_hands - k.
    for k in range(1, num_couples + 1):
        model.add_constr(hands[2 * k] + hands[2 * k + 1] == max_hands)

    # No objective: the question asks for a number that the constraints already fix.
    return model, {"hil": hands[0]}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
