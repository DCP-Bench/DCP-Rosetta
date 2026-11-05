"""Exodus: match five children with an age, a country and a part of the story; the same number in two lists means
the same child."""
import hexaly.optimizer as hx

AGES = [3, 5, 7, 8, 10]
BERNICE, CARL, DEBBY, SAMMY, TED = range(5)           # the children
ETHIOPIA, KAZAKHSTAN, LITHUANIA, MOROCCO, YEMEN = range(5)  # the countries
BURNING_BUSH, CAPTIVITY, MOSES_YOUTH, PASSOVER, COMMANDMENTS = range(5)  # the story parts


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    def group():
        """The numbers 1..5 given to the five items of a kind, all different."""
        numbers = [model.int(1, 5) for _ in range(5)]  # the number (1 to 5) given to each of the five items of a kind
        for a in range(5):
            for b in range(a + 1, 5):
                model.constraint(numbers[a] != numbers[b])
        return numbers

    # The ages are numbered in the order given, which fixes the numbering of the others
    ages = [1, 2, 3, 4, 5]
    children, countries, stories = group(), group(), group()

    def age_of(number):
        """The age of the child who has this number: the age whose slot carries it."""
        return model.sum(AGES[slot] * (ages[slot] == number) for slot in range(5))

    # 1. Debby's family is from Lithuania
    model.constraint(children[DEBBY] == countries[LITHUANIA])
    # 2. The child who told the Passover story is two years older than Bernice
    model.constraint(age_of(stories[PASSOVER]) == age_of(children[BERNICE]) + 2)
    # 3. The child from the Yemeni family is younger than the child from the Ethiopian family
    model.constraint(age_of(countries[YEMEN]) < age_of(countries[ETHIOPIA]))
    # 4. The child from the Moroccan family is three years older than Ted
    model.constraint(age_of(countries[MOROCCO]) == age_of(children[TED]) + 3)
    # 5. Sammy is three years older than the child who told the story of Moses's youth
    model.constraint(age_of(children[SAMMY]) == age_of(stories[MOSES_YOUTH]) + 3)

    return optimizer, {"ages": ages, "children": children, "countries": countries, "stories": stories}
