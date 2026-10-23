from hermax.model import Model

# Value order of each attribute, as listed in the problem statement.
AGES = [3, 5, 7, 8, 10]


def related(m, ages, house_a, house_b, pred):
    """Post: the child in house_a and the child in house_b have ages that satisfy pred.

    ages[a] is the house (1..5) of the child whose age is AGES[a].
    For every pair of ages that breaks pred, forbid that pair of houses.
    """
    for a in range(len(AGES)):
        for b in range(len(AGES)):
            if pred(AGES[a], AGES[b]):
                continue
            in_a = m.bool()
            in_b = m.bool()
            m &= (ages[a] == house_a).iff(in_a)
            m &= (ages[b] == house_b).iff(in_b)
            m &= (~in_a | ~in_b)


def build(instance):
    m = Model()
    ages = m.int_vector("ages", 5, 1, 5)
    children = m.int_vector("children", 5, 1, 5)
    countries = m.int_vector("countries", 5, 1, 5)
    stories = m.int_vector("stories", 5, 1, 5)

    m &= ages.all_different()
    m &= children.all_different()
    m &= countries.all_different()
    m &= stories.all_different()

    # Indices: children 0 Bernice, 1 Carl, 2 Debby, 3 Sammy, 4 Ted.
    # countries 0 Ethiopia, 1 Kazakhstan, 2 Lithuania, 3 Morocco, 4 Yemen.
    # stories 0 burning bush, 1 captivity, 2 Moses's youth, 3 Passover, 4 Ten Commandments.

    # 1. Debby's family is from Lithuania.
    m &= (children[2] == countries[2])

    # 2. The Passover child is two years older than Bernice.
    related(m, ages, stories[3], children[0], lambda x, y: x == y + 2)

    # 3. The Yemen child is younger than the Ethiopian child.
    related(m, ages, countries[4], countries[0], lambda x, y: x < y)

    # 4. The Moroccan child is three years older than Ted.
    related(m, ages, countries[3], children[4], lambda x, y: x == y + 3)

    # 5. Sammy is three years older than the child who told Moses's youth.
    related(m, ages, children[3], stories[2], lambda x, y: x == y + 3)

    return m, {
        "ages": ages,
        "children": children,
        "countries": countries,
        "stories": stories,
    }
