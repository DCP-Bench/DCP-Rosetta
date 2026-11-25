# session3_exodus: a FOX model for GroundFOX from DCP Rosetta.
#
# In preparation for Passover, five children at Hebrew school (Bernice, Carl, Debby, Sammy,
# and Ted) have been chosen to present different parts of the story of the Exodus from Egypt
# (burning bush, captivity, Moses’s youth, Passover, or the Ten Commandments). Each child is a
# different age (three, five, seven, eight, or ten), and the family of each child has recently
# made its own exodus to America from a different country (Ethiopia, Kazakhstan, Lithuania,
# Morocco, or Yemen). Can you find the age of each child, his or her family’s country of
# origin, and the part of the Exodus story each related? 1. Debby’s family is from Lithuania.
# 2. The child who told the story of the Passover is two years older than Bernice. 3. The
# child whose family is from Yemen is younger than the child from the Ethiopian family. 4. The
# child from the Moroccan family is three years older than Ted. 5. Sammy is three years older
# than the child who told the story of Moses’s youth in the house of the Pharaoh. Determine
# the association: Age-Child-Country-Story.
#
# Print the ages (ages), children (children), countries (countries), and stories (stories) as
# lists of integers from 1 to 5, where the same number represents a mapping between the four
# categories. The first slot in each list corresponds to the first entity as given in the
# problem statement, i.e., ages[0] corresponds to three, children[0] corresponds to Bernice,
# countries[0] corresponds to Ethiopia, and stories[0] corresponds to burning bush.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_exodus.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py session3_exodus.json --check

# session3_exodus: a FOX model for GroundFOX from DCP Rosetta.
#
# Five children (Bernice, Carl, Debby, Sammy, Ted) with ages 3, 5, 7, 8, 10, families from Ethiopia,
# Kazakhstan, Lithuania, Morocco, Yemen, and Exodus stories (burning bush, captivity, Moses's youth,
# Passover, Ten Commandments). Each category is a bijection onto the houses 1..5; the same house number
# links the items of one child. Print ages, children, countries, stories: ages[i] is the house of the
# age VALS[i], children[j] the house of child j, and so on.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

VALS = [3, 5, 7, 8, 10]

CATS = ["ages", "children", "countries", "stories"]


def _theory():
    lines = []
    for cat in CATS:
        lines.append(f"    ! x [Ix(x)] : ? h [Hs(h)] : {cat}(x,h).")
        lines.append(f"    ! x [Ix(x)] : ! h [Hs(h)] : ! g [Hs(g) & ~(h = g)] : ~{cat}(x,h) | ~{cat}(x,g).")
        lines.append(f"    ! h [Hs(h)] : ! x [Ix(x)] : ! y [Ix(y) & ~(x = y)] : ~{cat}(x,h) | ~{cat}(y,h).")

    def same(c1, x, c2, y):
        # Item x of category c1 and item y of category c2 belong to the same house.
        lines.append(f"    ! h [Hs(h)] : ~{c1}({x},h) | {c2}({y},h).")
        lines.append(f"    ! h [Hs(h)] : ~{c2}({y},h) | {c1}({x},h).")

    def rel(c1, x, c2, y, r):
        # The age of the item x (category c1) stands in relation r (Older2, Older3, Less) to the age of y (c2).
        lines.append(
            f"    ! h [Hs(h)] : ! g [Hs(g)] : ! a [Ix(a)] : ! b [Ix(b) & ~{r}(a,b)] : "
            f"~{c1}({x},h) | ~{c2}({y},g) | ~ages(a,h) | ~ages(b,g)."
        )

    # Debby's family is from Lithuania.
    same("children", 2, "countries", 2)
    # The Passover child is two years older than Bernice.
    rel("stories", 3, "children", 0, "Older2")
    # The Yemen child is younger than the Ethiopian child.
    rel("countries", 4, "countries", 0, "Less")
    # The Moroccan child is three years older than Ted.
    rel("countries", 3, "children", 4, "Older3")
    # Sammy is three years older than the Moses's-youth child.
    rel("children", 3, "stories", 2, "Older3")
    return "\n".join(lines)


FOX = (
    "\ninvocabulary { Ix/1 Hs/1 Older2/2 Older3/2 Less/2 }\n"
    "outvocabulary { ages/2 children/2 countries/2 stories/2 }\n"
    "theory {\n" + _theory() + "\n}\n"
)


def structure(instance):
    idx = range(len(VALS))
    return {
        "Ix": list(idx),
        "Hs": [1, 2, 3, 4, 5],
        "Older2": [(a, b) for a in idx for b in idx if VALS[a] == VALS[b] + 2],
        "Older3": [(a, b) for a in idx for b in idx if VALS[a] == VALS[b] + 3],
        "Less": [(a, b) for a in idx for b in idx if VALS[a] < VALS[b]],
    }
