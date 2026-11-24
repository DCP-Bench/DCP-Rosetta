# session3_exodus: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_exodus.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python session3_exodus.py

from pycsp3 import *


def create_model(instance):
    """Five children at Hebrew school each tell one part of the Exodus story. Each child
    is a different age (three, five, seven, eight or ten), and each family made its exodus
    from a different country (Ethiopia, Kazakhstan, Lithuania, Morocco or Yemen). Find the
    age, country of origin and story of each child. Clues: Debby's family is from
    Lithuania; the child who told the story of the Passover is two years older than
    Bernice; the child whose family is from Yemen is younger than the child from the
    Ethiopian family; the child from the Moroccan family is three years older than Ted;
    Sammy is three years older than the child who told the story of Moses's youth in the
    house of the Pharaoh."""
    # The children, in the order of the statement: child_index[name] is the child's position.
    child_index = {"Bernice": 0, "Carl": 1, "Debby": 2, "Sammy": 3, "Ted": 4}
    n_children = len(child_index)

    # The possible ages in years, in increasing order: age slot a is age_years[a].
    age_years = [3, 5, 7, 8, 10]
    # The pairs (age slot, age in years), built once for the age tables below.
    age_table = list(enumerate(age_years))

    # The countries of origin and the stories, each by its position in the statement's list.
    country_index = {"Ethiopia": 0, "Kazakhstan": 1, "Lithuania": 2, "Morocco": 3, "Yemen": 4}
    story_index = {"burning bush": 0, "captivity": 1, "Moses's youth": 2, "Passover": 3, "Ten Commandments": 4}

    # child_age[c] is the age in years of child c.
    child_age = VarArray(size=n_children, dom=set(age_years))
    # child_age_slot[c] is the position of child c's age in age_years.
    child_age_slot = VarArray(size=n_children, dom=range(n_children))
    # child_country_slot[c] is the position in country_index of child c's country of origin.
    child_country_slot = VarArray(size=n_children, dom=range(n_children))
    # child_story_slot[c] is the position in story_index of the story child c told.
    child_story_slot = VarArray(size=n_children, dom=range(n_children))

    # children[c] is the number given to child c; the numbering of the children is free: any
    # distinct numbers 1 to n_children are a valid answer, since the same number marks the same
    # child in every list.
    children = VarArray(size=n_children, dom=range(1, n_children + 1))
    # ages[a] is the number of the child who is age_years[a].
    ages = VarArray(size=n_children, dom=range(1, n_children + 1))
    # countries[k] is the number of the child whose family comes from country k.
    countries = VarArray(size=n_children, dom=range(1, n_children + 1))
    # stories[s] is the number of the child who told story s.
    stories = VarArray(size=n_children, dom=range(1, n_children + 1))

    debby = child_index["Debby"]
    bernice = child_index["Bernice"]
    ted = child_index["Ted"]
    sammy = child_index["Sammy"]
    passover = story_index["Passover"]
    moses_youth = story_index["Moses's youth"]
    lithuania = country_index["Lithuania"]
    yemen = country_index["Yemen"]
    ethiopia = country_index["Ethiopia"]
    morocco = country_index["Morocco"]

    satisfy(
        # Each child has a different age, country and story.
        AllDifferent(child_age_slot),
        AllDifferent(child_country_slot),
        AllDifferent(child_story_slot),
        AllDifferent(children),
        # The age of each child is the age in years of its slot (a Python list cannot be indexed by a variable).
        [Table(scope=[child_age_slot[c], child_age[c]], supports=age_table) for c in range(n_children)],
        # The lists give, for each age, country and story, the number of the child who has it.
        [ages[child_age_slot[c]] == children[c] for c in range(n_children)],
        [countries[child_country_slot[c]] == children[c] for c in range(n_children)],
        [stories[child_story_slot[c]] == children[c] for c in range(n_children)],
        # Debby's family is from Lithuania.
        child_country_slot[debby] == lithuania,
        # The child who told the story of the Passover is two years older than Bernice.
        [
            imply(child_story_slot[c] == passover, child_age[c] == child_age[bernice] + 2)
            for c in range(n_children)
        ],
        # The child whose family is from Yemen is younger than the child from the Ethiopian family.
        [
            imply(
                (child_country_slot[c] == yemen) & (child_country_slot[d] == ethiopia),
                child_age[c] < child_age[d],
            )
            for c in range(n_children)
            for d in range(n_children)
        ],
        # The child from the Moroccan family is three years older than Ted.
        [
            imply(child_country_slot[c] == morocco, child_age[c] == child_age[ted] + 3)
            for c in range(n_children)
        ],
        # Sammy is three years older than the child who told the story of Moses's youth.
        [
            imply(child_story_slot[c] == moses_youth, child_age[sammy] == child_age[c] + 3)
            for c in range(n_children)
        ],
    )

    return {"ages": ages, "children": children, "countries": countries, "stories": stories}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
