# session3_kidney_exchange: a CPMpy model from DCP Rosetta.
# Download the `session3_kidney_exchange.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_kidney_exchange.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python session3_kidney_exchange.py session3_kidney_exchange.json

import cpmpy as cp


def create_model(instance):
    """People on a hospital waiting list for a kidney can donate to some of the
    others, as given by a directed compatibility graph. Maximize the number of
    people who receive a kidney: anyone who gives a kidney must receive one, and
    nobody receives more than one."""
    num_people = instance["num_people"]  # the number of people on the waiting list, numbered 1..num_people
    compatible = instance["compatible"]  # compatible[i]: the (1-based) people that person i+1 can donate to

    # transplants[i, j] is true when person i donates a kidney to person j (0-based indices)
    transplants = cp.boolvar(shape=(num_people, num_people), name="transplants")
    gives = transplants.sum(axis=1)  # gives[i]: the number of kidneys person i donates
    receives = transplants.sum(axis=0)  # receives[i]: the number of kidneys person i receives

    model = cp.Model()
    # Nobody gives more than one kidney, and nobody receives more than one.
    model.add(gives <= 1)
    model.add(receives <= 1)
    # Anyone who gives a kidney must receive one (both counts are 0 or 1 here).
    model.add(gives <= receives)
    # A kidney can only go to a compatible person.
    for i in range(num_people):
        for j in range(num_people):
            if j + 1 not in compatible[i]:
                model.add(transplants[i, j] == 0)
    # Maximize the number of transplants, which is the number of people receiving a kidney.
    model.maximize(cp.sum(transplants))

    return model, {"transplants": transplants}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
