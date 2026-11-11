# general_store: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/general_store.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python general_store.py

from docplex.mp.model import Model


def create_model(instance):
    """Each different letter stands for a different digit, and the sixteen words above the line
    add up to ALL WOOL. Leading zeros are allowed: a word may start with the digit 0."""
    letters = "CHESABOWPL"  # the ten letters of the sign
    # the words above the line
    addends = ["CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
               "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"]
    total = "ALLWOOL"  # the word below the line
    digits = range(10)  # the digits 0..9

    model = Model("general_store")

    # is_digit[c, d] is 1 when letter c stands for digit d; each letter is one digit and
    # different letters are different digits.
    is_digit = {(c, d): model.binary_var(name=f"{c}_is_{d}") for c in letters for d in digits}
    model.add_constraints(model.sum(is_digit[c, d] for d in digits) == 1 for c in letters)
    model.add_constraints(model.sum(is_digit[c, d] for c in letters) <= 1 for d in digits)
    # value[c] is the digit that letter c stands for
    value = {c: model.integer_var(0, 9, name=c) for c in letters}
    model.add_constraints(value[c] == model.sum(d * is_digit[c, d] for d in digits) for c in letters)

    def word(w):
        # The number a word spells, most significant letter first.
        return model.sum(10 ** (len(w) - 1 - k) * value[ch] for k, ch in enumerate(w))

    # The words above the line add up to ALL WOOL.
    model.add_constraint(model.sum(word(w) for w in addends) == word(total))

    return model, dict(value)


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
