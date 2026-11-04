# general_store: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/general_store.html
# Run it (after `pip install ortools`) with:
#   python general_store.py

from ortools.sat.python import cp_model


def create_model(instance):
    """The owner of a general store has put up a sign: sixteen words that add up to
    'ALL WOOL'. Each different letter stands for a different digit; find the digit
    of every letter."""
    # The words that are added.
    words = ["CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
             "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"]
    total = "ALLWOOL"  # the total the words make

    model = cp_model.CpModel()

    # The letters of the words and the total, each once.
    letters = list(dict.fromkeys("".join(words + [total])))
    # digit[c] is the digit that letter c stands for
    digit = {c: model.new_int_var(0, 9, c) for c in letters}

    def value(word):
        # The number a word spells: its last letter is the units digit, the one before it the tens, and so on.
        return sum(10 ** k * digit[c] for k, c in enumerate(reversed(word)))

    # Different letters stand for different digits.
    model.add_all_different([digit[c] for c in letters])

    # The words add up to the total.
    model.add(sum(value(word) for word in words) == value(total))

    return model, {c: digit[c] for c in letters}


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
