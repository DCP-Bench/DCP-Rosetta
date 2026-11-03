# zebra: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/zebra.html
# Run it (after `pip install hermax`) with:
#   python zebra.py

from hermax.model import Model


def create_model(instance):
    """The Zebra puzzle (Einstein's puzzle): five houses in a row, numbered 0 (left) to 4
    (right). Each house has a different colour, nationality, pet, drink and job, and the
    clues below say which house each person, pet and drink is in. Find the house of every
    colour, nationality, pet, drink and job.

    The puzzle fixes all its data in the statement, so the instance is empty: the model
    reads nothing from it.
    """
    # Every category is a vector of five integers: entry k is the house (0..4) of its
    # k-th member, in the order listed in the statement.
    # colors: yellow, green, red, white, blue
    # nations: italy, spain, japan, england, norway
    # pets: cat, zebra, bear, snails, horse
    # drinks: milk, water, tea, coffee, juice
    # jobs: painter, sculptor, diplomat, pianist, doctor
    m = Model()
    colors = m.int_vector("colors", 5, 0, 4)    # colors[c]: the house painted colour c
    nations = m.int_vector("nations", 5, 0, 4)  # nations[n]: the house of the person of nation n
    pets = m.int_vector("pets", 5, 0, 4)        # pets[p]: the house of the owner of pet p
    drinks = m.int_vector("drinks", 5, 0, 4)    # drinks[d]: the house of the person who drinks d
    jobs = m.int_vector("jobs", 5, 0, 4)        # jobs[j]: the house of the person with job j

    # Each house has one inhabitant, one colour, one pet, one drink and one job, so
    # every category occupies five different houses.
    for vec in (colors, nations, pets, drinks, jobs):
        m &= vec.all_different()

    # Index constants for the members of each category, as listed above.
    yellow, green, red, white, blue = range(5)
    italy, spain, japan, england, norway = range(5)
    cat, zebra, bear, snails, horse = range(5)
    milk, water, tea, coffee, juice = range(5)
    painter, sculptor, diplomat, pianist, doctor = range(5)

    # The painter owns the horse.
    m &= (jobs[painter] == pets[horse])
    # The diplomat drinks coffee.
    m &= (jobs[diplomat] == drinks[coffee])
    # The one who drinks milk lives in the white house.
    m &= (drinks[milk] == colors[white])
    # The Spaniard is a painter.
    m &= (nations[spain] == jobs[painter])
    # The Englishman lives in the red house.
    m &= (nations[england] == colors[red])
    # The snails are owned by the sculptor.
    m &= (pets[snails] == jobs[sculptor])
    # The green house is immediately on the left of the red one.
    m &= (colors[green] + 1 == colors[red])
    # The Norwegian lives immediately on the right of the blue house.
    m &= (nations[norway] == colors[blue] + 1)
    # The doctor drinks milk.
    m &= (jobs[doctor] == drinks[milk])
    # The diplomat is Japanese.
    m &= (jobs[diplomat] == nations[japan])
    # The Norwegian owns the zebra.
    m &= (nations[norway] == pets[zebra])
    # The green house is next to the white one, on either side. Two Booleans say which
    # side; at least one must hold.
    white_right_of_green = m.bool()  # true when the white house is just right of the green one
    green_right_of_white = m.bool()  # true when the green house is just right of the white one
    m &= (colors[white] == colors[green] + 1).iff(white_right_of_green)
    m &= (colors[green] == colors[white] + 1).iff(green_right_of_white)
    m &= (white_right_of_green | green_right_of_white)
    # The horse is owned by the neighbour of the diplomat, on either side.
    horse_right_of_diplomat = m.bool()  # true when the horse owner lives just right of the diplomat
    diplomat_right_of_horse = m.bool()  # true when the diplomat lives just right of the horse owner
    m &= (pets[horse] == jobs[diplomat] + 1).iff(horse_right_of_diplomat)
    m &= (jobs[diplomat] == pets[horse] + 1).iff(diplomat_right_of_horse)
    m &= (horse_right_of_diplomat | diplomat_right_of_horse)
    # The Italian lives in the red, white or green house.
    italy_in_red = m.bool()    # true when the Italian lives in the red house
    italy_in_white = m.bool()  # true when the Italian lives in the white house
    italy_in_green = m.bool()  # true when the Italian lives in the green house
    m &= (colors[red] == nations[italy]).iff(italy_in_red)
    m &= (colors[white] == nations[italy]).iff(italy_in_white)
    m &= (colors[green] == nations[italy]).iff(italy_in_green)
    m &= (italy_in_red | italy_in_white | italy_in_green)

    # The puzzle has no objective: any assignment satisfying the clues is the answer.
    return m, {"colors": colors, "nations": nations, "pets": pets, "drinks": drinks, "jobs": jobs}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
