# session3_exodus: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_exodus.html
# Run it (after `pip install hermax`) with:
#   python session3_exodus.py

from itertools import product

from hermax.model import Model

# The five children, in the order the statement lists them. Each is an index 0..4.
BERNICE, CARL, DEBBY, SAMMY, TED = range(5)
# The five ages, in the order the statement lists them (three, five, seven, eight, ten).
AGE_VALUES = [3, 5, 7, 8, 10]
# The five countries, as indices 0..4 in the order the statement lists them.
ETHIOPIA, KAZAKHSTAN, LITHUANIA, MOROCCO, YEMEN = range(5)
# The five parts of the story, as indices 0..4 in the order the statement lists them.
BURNING_BUSH, CAPTIVITY, MOSES_YOUTH, PASSOVER, TEN_COMMANDMENTS = range(5)
N = 5


def create_model(instance):
    """Exodus puzzle: five children at Hebrew school each tell a different part of the Exodus
    story, are of different ages, and come from families that emigrated from different
    countries. Find the age, the child, the country and the story of each of the five
    entities from five clues. The statement fixes all the data, so the instance is empty
    and no field is read."""
    m = Model()

    # Output: children[k] is the shared number (1..5) of the entity in slot k of the children
    # list. The same number in ages, countries and stories marks the one person.
    children = m.int_vector("children", N, 1, N)
    # Output: ages[k] is the number of the person who is AGE_VALUES[k] years old.
    ages = m.int_vector("ages", N, 1, N)
    # Output: countries[k] is the number of the person whose family is from country k.
    countries = m.int_vector("countries", N, 1, N)
    # Output: stories[k] is the number of the person who told story k.
    stories = m.int_vector("stories", N, 1, N)

    # Per child c: the index into AGE_VALUES of c's age.
    age_index = m.int_vector("age_index", N, 0, N - 1)
    # Per child c: the index of the country c's family comes from.
    country_index = m.int_vector("country_index", N, 0, N - 1)
    # Per child c: the index of the part of the story c told.
    story_index = m.int_vector("story_index", N, 0, N - 1)

    # Each category's five slots are five different people, so each list is a permutation.
    m &= children.all_different()
    m &= ages.all_different()
    m &= countries.all_different()
    m &= stories.all_different()
    m &= age_index.all_different()
    m &= country_index.all_different()
    m &= story_index.all_different()

    # Link the per-child indices to the output lists: child c's number is the entry of the
    # age, country and story list at c's own index.
    for c in range(N):
        m &= (ages[age_index[c]] == children[c])
        m &= (countries[country_index[c]] == children[c])
        m &= (stories[story_index[c]] == children[c])

    def clue_table(variables, holds):
        """The combinations of values of these variables that satisfy the clue (holds)."""
        rows = [values for values in product(range(N), repeat=len(variables))
                if holds(*values)]
        return m.table(variables, allowed=rows)

    # 1. Debby's family is from Lithuania.
    m &= (country_index[DEBBY] == LITHUANIA)

    # 2. The child who told the Passover story is two years older than Bernice.
    #    Bernice cannot be two years older than herself, so she did not tell it.
    m &= (story_index[BERNICE] != PASSOVER)
    for c in range(N):
        if c != BERNICE:
            m &= clue_table([story_index[c], age_index[c], age_index[BERNICE]],
                            lambda s, a, b: s != PASSOVER or AGE_VALUES[a] == AGE_VALUES[b] + 2)

    # 3. The child whose family is from Yemen is younger than the child from the Ethiopian family.
    for c in range(N):
        for d in range(N):
            if c != d:
                m &= clue_table([country_index[c], country_index[d], age_index[c], age_index[d]],
                                lambda yc, ed, ac, ad: (not (yc == YEMEN and ed == ETHIOPIA)
                                                        or AGE_VALUES[ac] < AGE_VALUES[ad]))

    # 4. The child from the Moroccan family is three years older than Ted.
    #    Ted is not from Morocco, since no one is three years older than himself.
    m &= (country_index[TED] != MOROCCO)
    for c in range(N):
        if c != TED:
            m &= clue_table([country_index[c], age_index[c], age_index[TED]],
                            lambda mo, a, t: mo != MOROCCO or AGE_VALUES[a] == AGE_VALUES[t] + 3)

    # 5. Sammy is three years older than the child who told the story of Moses's youth.
    #    Sammy did not tell that story, since no one is three years older than himself.
    m &= (story_index[SAMMY] != MOSES_YOUTH)
    for c in range(N):
        if c != SAMMY:
            m &= clue_table([story_index[c], age_index[SAMMY], age_index[c]],
                            lambda s, sa, a: s != MOSES_YOUTH or AGE_VALUES[sa] == AGE_VALUES[a] + 3)

    # The puzzle is a satisfaction problem: there is no objective.
    return m, {"ages": ages, "children": children, "countries": countries, "stories": stories}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
