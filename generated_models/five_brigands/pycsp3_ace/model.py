# five_brigands: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_brigands.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python five_brigands.py

from pycsp3 import *


def create_model(instance):
    """Five Spanish brigands, Alfonso, Benito, Carlos, Diego and Esteban, captured
    altogether exactly 200 doubloons. If Alfonso had twelve times as much, Benito three
    times as much, Carlos the same amount, Diego half as much and Esteban one-third as
    much, they would still have altogether just 200 doubloons. How many doubloons had
    each? No brigand had less than one doubloon."""
    total_doubloons = 200

    # Doubloons Alfonso had; at least one (stated), at most the total (assumed: the five shares add up to it).
    alfonso = Var(dom=range(1, total_doubloons + 1))
    # Doubloons Benito had; bounds as for Alfonso.
    benito = Var(dom=range(1, total_doubloons + 1))
    # Doubloons Carlos had; bounds as for Alfonso.
    carlos = Var(dom=range(1, total_doubloons + 1))
    # Doubloons Diego had; bounds as for Alfonso.
    diego = Var(dom=range(1, total_doubloons + 1))
    # Doubloons Esteban had; bounds as for Alfonso. The output key is E, a reserved identifier in the solver, so the variable is named for its brigand.
    esteban = Var(dom=range(1, total_doubloons + 1))

    satisfy(
        # The five brigands had exactly 200 doubloons altogether.
        alfonso + benito + carlos + diego + esteban == total_doubloons,
        # With the changed amounts (12 x Alfonso, 3 x Benito, Carlos, Diego / 2, Esteban / 3)
        # the total is still 200. Both sides are multiplied by 6, so the halves and thirds
        # become whole numbers: 12 * 6 = 72, 3 * 6 = 18, 1 * 6 = 6, 6 / 2 = 3, 6 / 3 = 2.
        72 * alfonso + 18 * benito + 6 * carlos + 3 * diego + 2 * esteban == 6 * total_doubloons,
    )

    return {"A": alfonso, "B": benito, "C": carlos, "D": diego, "E": esteban}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
