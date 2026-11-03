"""Zebra puzzle: five houses in a row, each with a colour, an inhabitant of some nation, a pet, a drink and a job."""
import hexaly.optimizer as hx

YELLOW, GREEN, RED, WHITE, BLUE = range(5)
ITALY, SPAIN, JAPAN, ENGLAND, NORWAY = range(5)
CAT, ZEBRA, BEAR, SNAILS, HORSE = range(5)
MILK, WATER, TEA, COFFEE, JUICE = range(5)
PAINTER, SCULPTOR, DIPLOMAT, PIANIST, DOCTOR = range(5)


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    def group():
        """The house (0 to 4, left to right) of each of five items of a kind, all different."""
        houses = [model.int(0, 4) for _ in range(5)]  # the house (0 to 4, left to right) of each of five items of a kind
        for a in range(5):
            for b in range(a + 1, 5):
                model.constraint(houses[a] != houses[b])
        return houses

    colors, nations, pets, drinks, jobs = group(), group(), group(), group(), group()

    model.constraint(jobs[PAINTER] == pets[HORSE])                 # the painter owns the horse
    model.constraint(jobs[DIPLOMAT] == drinks[COFFEE])             # the diplomat drinks coffee
    model.constraint(drinks[MILK] == colors[WHITE])                # the milk drinker lives in the white house
    model.constraint(nations[SPAIN] == jobs[PAINTER])              # the Spaniard is a painter
    model.constraint(nations[ENGLAND] == colors[RED])              # the Englishman lives in the red house
    model.constraint(pets[SNAILS] == jobs[SCULPTOR])               # the snails are owned by the sculptor
    model.constraint(colors[GREEN] + 1 == colors[RED])             # green is immediately left of red
    model.constraint(nations[NORWAY] == colors[BLUE] + 1)          # the Norwegian is immediately right of blue
    model.constraint(jobs[DOCTOR] == drinks[MILK])                 # the doctor drinks milk
    model.constraint(jobs[DIPLOMAT] == nations[JAPAN])             # the diplomat is Japanese
    model.constraint(nations[NORWAY] == pets[ZEBRA])               # the Norwegian owns the zebra
    model.constraint(model.abs(colors[GREEN] - colors[WHITE]) == 1)  # green is next to white
    model.constraint(model.abs(pets[HORSE] - jobs[DIPLOMAT]) == 1)  # the horse's owner neighbours the diplomat
    # the Italian lives in the red, white or green house
    model.constraint(model.or_(nations[ITALY] == colors[RED], nations[ITALY] == colors[WHITE],
                               nations[ITALY] == colors[GREEN]))

    return optimizer, {"colors": colors, "nations": nations, "jobs": jobs, "pets": pets, "drinks": drinks}
