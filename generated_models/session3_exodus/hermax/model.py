# session3_exodus: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_exodus.html
# Run it (after `pip install hermax`) with:
#   python session3_exodus.py

from hermax.model import Model

# The five children, in the order the statement lists them. Each is an index 0..4.
BERNICE, CARL, DEBBY, SAMMY, TED = range(5)
# The five ages, in the order the statement lists them (three, five, seven, eight, ten).
AGE_VALUES = [3, 5, 7, 8, 10]
# The five countries, as indices 0..4 in the order the statement lists them.
ETHIOPIA, KAZAKHSTAN, LITHUANIA, MOROCCO, YEMEN = range(5)
# The five parts of the story, as indices 0..4 in the order the statement lists them.
BURNING_BUSH, CAPTIVITY, MOSES_YOUTH, PASSOVER, TEN_COMMANDMENTS = range(5)
# N is the number of children, and equally the number of ages, countries and story parts.
N = 5


def create_model(instance):
    """Exodus puzzle: five children at Hebrew school each tell a different part of the Exodus
    story, are of different ages, and come from families that emigrated from different
    countries. Find the age, the country and the story of each child from five clues.
    The statement fixes all the data, so the instance is empty and no field is read."""
    m = Model()

    # Output: children[k] is the shared number (1..5) of the child in slot k of the children
    # list. The same number in ages, countries and stories marks the one child.
    children = m.int_vector("children", N, 1, N)
    # Output: ages[k] is the number of the child who is AGE_VALUES[k] years old.
    ages = m.int_vector("ages", N, 1, N)
    # Output: countries[k] is the number of the child whose family is from country k.
    countries = m.int_vector("countries", N, 1, N)
    # Output: stories[k] is the number of the child who told story k.
    stories = m.int_vector("stories", N, 1, N)

    # Per child c: the index into AGE_VALUES of c's age, and the age in years itself.
    age_index = m.int_vector("age_index", N, 0, N - 1)
    age = m.int_vector("age", N, min(AGE_VALUES), max(AGE_VALUES))
    # Per child c: the index of the country c's family comes from.
    country_index = m.int_vector("country_index", N, 0, N - 1)
    # Per child c: the index of the part of the story c told.
    story_index = m.int_vector("story_index", N, 0, N - 1)

    # The children are distinct, and each per-child index is a permutation (every age,
    # country and story is used once). The output lists then are permutations of the
    # children numbers through the links below, so they need no all_different of their own.
    m &= children.all_different()
    m &= age_index.all_different()
    m &= country_index.all_different()
    m &= story_index.all_different()

    # Link the per-child indices to the output lists: child c's number is the entry of the
    # age, country and story list at c's own index; and age[c] is the years at age_index[c].
    for c in range(N):
        m &= (ages[age_index[c]] == children[c])
        m &= (countries[country_index[c]] == children[c])
        m &= (stories[story_index[c]] == children[c])
        m &= ((AGE_VALUES @ age_index[c]) == age[c])

    # 1. Debby's family is from Lithuania.
    m &= (country_index[DEBBY] == LITHUANIA)

    # 2. The child who told the Passover story is two years older than Bernice.
    #    Bernice cannot be two years older than herself, so she did not tell it.
    m &= (story_index[BERNICE] != PASSOVER)
    for c in range(N):
        if c != BERNICE:
            m &= (age[c] == age[BERNICE] + 2).only_if(story_index[c] == PASSOVER)

    # 3. The child whose family is from Yemen is younger than the child from the Ethiopian family.
    #    A half-reified condition must be a single literal, so it cannot be "c is from Yemen and
    #    d is from Ethiopia" at once: name the ages of the two children instead.
    yemen_age = m.int("yemen_age", min(AGE_VALUES), max(AGE_VALUES))
    ethiopia_age = m.int("ethiopia_age", min(AGE_VALUES), max(AGE_VALUES))
    for c in range(N):
        m &= (age[c] == yemen_age).only_if(country_index[c] == YEMEN)
        m &= (age[c] == ethiopia_age).only_if(country_index[c] == ETHIOPIA)
    m &= (yemen_age < ethiopia_age)

    # 4. The child from the Moroccan family is three years older than Ted.
    #    Ted is not from Morocco, since no one is three years older than himself.
    m &= (country_index[TED] != MOROCCO)
    for c in range(N):
        if c != TED:
            m &= (age[c] == age[TED] + 3).only_if(country_index[c] == MOROCCO)

    # 5. Sammy is three years older than the child who told the story of Moses's youth.
    #    Sammy did not tell that story, since no one is three years older than himself.
    m &= (story_index[SAMMY] != MOSES_YOUTH)
    for c in range(N):
        if c != SAMMY:
            m &= (age[SAMMY] == age[c] + 3).only_if(story_index[c] == MOSES_YOUTH)

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
