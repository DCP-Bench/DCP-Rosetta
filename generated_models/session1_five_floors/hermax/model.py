# session1_five_floors: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_five_floors.html
# Run it (after `pip install hermax`) with:
#   python session1_five_floors.py

from hermax.model import Model


def create_model(instance):
    """Baker, Cooper, Fletcher, Miller and Smith live on different floors, 1 to 5, of a
    five-floor apartment house. The clues rule out some floors and some neighbouring
    floors. Find the floor of each person. This is a satisfaction problem: the problem
    fixes all the data, so the instance carries nothing and is not read."""
    m = Model()

    # B, C, F, M, S: the floor (1 to 5) where Baker, Cooper, Fletcher, Miller and Smith live
    B, C, F, M, S = (m.int(name, 1, 5) for name in "BCFMS")

    # They all live on different floors.
    m &= m.vector([B, C, F, M, S]).all_different()

    # Baker does not live on the fifth floor.
    m &= (B != 5)
    # Cooper does not live on the first floor.
    m &= (C != 1)
    # Fletcher lives on neither the fifth nor the first floor.
    m &= (F != 5)
    m &= (F != 1)
    # Miller lives on a higher floor than Cooper.
    m &= (C < M)

    # Smith does not live on a floor adjacent to Fletcher's, so the two are at least two
    # floors apart. A Boolean says which of the two is the higher one.
    smith_higher = m.bool()  # true when Smith is above Fletcher
    m &= (F + 2 <= S).only_if(smith_higher)
    m &= (S + 2 <= F).only_if(~smith_higher)

    # Fletcher does not live on a floor adjacent to Cooper's, so the two are at least two
    # floors apart. A Boolean says which of the two is the higher one.
    fletcher_higher = m.bool()  # true when Fletcher is above Cooper
    m &= (C + 2 <= F).only_if(fletcher_higher)
    m &= (F + 2 <= C).only_if(~fletcher_higher)

    # No objective: any assignment that satisfies every clue is an answer.
    return m, {"B": B, "C": C, "F": F, "M": M, "S": S}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
