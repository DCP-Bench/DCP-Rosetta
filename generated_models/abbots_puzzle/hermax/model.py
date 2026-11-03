# abbots_puzzle: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install hermax`) with:
#   python abbots_puzzle.py
from hermax.model import Model


def create_model(instance):
    """Abbot's puzzle: 100 bushels of corn are shared among 100 people. Each man gets three
    bushels, each woman two and each child half a bushel, and there are five times as many
    women as men. Find the number of men, women and children.

    The puzzle has no instance data: the 100 people, the 100 bushels and the factor of five
    are part of the statement, so they are written as constants below."""
    m = Model()

    # men, women, children: how many people of each kind (no more than the 100 people)
    men = m.int("men", 0, 100)
    women = m.int("women", 0, 100)
    children = m.int("children", 0, 100)

    # The 100 people are men, women and children.
    m &= (men + women + children == 100)

    # The 100 bushels are shared out: 3 per man, 2 per woman, half a bushel per child.
    # Counted in half bushels so that every coefficient is an integer:
    # 6 per man, 4 per woman, 1 per child, 200 half bushels in all.
    m &= (6 * men + 4 * women + children == 200)

    # There are five times as many women as men.
    m &= (women == 5 * men)

    # No objective: any assignment that meets the three conditions answers the puzzle.
    return m, {"children": children, "men": men, "women": women}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
