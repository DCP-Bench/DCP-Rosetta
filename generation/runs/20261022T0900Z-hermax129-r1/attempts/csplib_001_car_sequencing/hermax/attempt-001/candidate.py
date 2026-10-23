from hermax.model import Model


def build(instance):
    # Read instance parameters
    at_most = instance["at_most"]
    per_slots = instance["per_slots"]
    demand = instance["demand"]
    requires = instance["requires"]

    num_stations = len(at_most)
    num_car_types = len(demand)
    total_cars = sum(demand)

    m = Model()

    # Create the sequence: sequence[i] is the car type for position i
    sequence = m.int_vector("sequence", total_cars, 0, num_car_types - 1)

    # Constraint 1: Each car type appears exactly demand[c] times in the sequence.
    # Count how many times each car type appears
    for c in range(num_car_types):
        count = 0
        for i in range(total_cars):
            count += (sequence[i] == c)
        m &= (count == demand[c])

    # Constraint 2: Sliding window capacity constraints.
    # For each station, in any consecutive window of per_slots[s] cars,
    # at most at_most[s] can require the option for that station
    for s in range(num_stations):
        window_size = per_slots[s]
        max_cars = at_most[s]

        # Iterate through all sliding windows of size window_size
        for start in range(total_cars - window_size + 1):
            # Count cars in this window that require option s
            window_sum = 0
            for pos in range(start, start + window_size):
                # Add 1 if the car at position pos requires option s
                for car_type in range(num_car_types):
                    if requires[car_type][s] == 1:
                        # Check if sequence[pos] == car_type
                        window_sum += (sequence[pos] == car_type)

            # Constraint: at most max_cars in this window
            m &= (window_sum <= max_cars)

    return m, {"sequence": sequence}
