from hermax.model import Model


def build(instance):
    # Houses are numbered 0 (left) to 4 (right). Each category lists the house of each of
    # its five members, in the order given in the description.
    # colors: yellow, green, red, white, blue
    # nations: italy, spain, japan, england, norway
    # pets: cat, zebra, bear, snails, horse
    # drinks: milk, water, tea, coffee, juice
    # jobs: painter, sculptor, diplomat, pianist, doctor
    m = Model()
    colors = m.int_vector("colors", 5, 0, 4)
    nations = m.int_vector("nations", 5, 0, 4)
    pets = m.int_vector("pets", 5, 0, 4)
    drinks = m.int_vector("drinks", 5, 0, 4)
    jobs = m.int_vector("jobs", 5, 0, 4)

    # Each category occupies five different houses.
    for vec in (colors, nations, pets, drinks, jobs):
        m &= vec.all_different()

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
    # The green house is next to the white one.
    right_of_green = m.bool()
    left_of_green = m.bool()
    m &= (colors[white] == colors[green] + 1).iff(right_of_green)
    m &= (colors[green] == colors[white] + 1).iff(left_of_green)
    m &= (right_of_green | left_of_green)
    # The horse is owned by the neighbour of the diplomat.
    horse_right = m.bool()
    horse_left = m.bool()
    m &= (pets[horse] == jobs[diplomat] + 1).iff(horse_right)
    m &= (jobs[diplomat] == pets[horse] + 1).iff(horse_left)
    m &= (horse_right | horse_left)
    # The Italian lives in the red, white or green house.
    italy_red = m.bool()
    italy_white = m.bool()
    italy_green = m.bool()
    m &= (colors[red] == nations[italy]).iff(italy_red)
    m &= (colors[white] == nations[italy]).iff(italy_white)
    m &= (colors[green] == nations[italy]).iff(italy_green)
    m &= (italy_red | italy_white | italy_green)

    return m, {"colors": colors, "nations": nations, "pets": pets, "drinks": drinks, "jobs": jobs}
