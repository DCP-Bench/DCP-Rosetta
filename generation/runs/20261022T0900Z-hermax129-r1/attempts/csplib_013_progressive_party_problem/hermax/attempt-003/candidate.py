from hermax.model import Model


def build(instance):
    # Progressive party problem: schedule visits to minimize number of host boats.

    n_boats = instance["n_boats"]
    n_periods = instance["n_periods"]
    capacity = instance["capacity"]
    crew_size = instance["crew_size"]

    m = Model()

    # Decision variables
    is_host = m.bool_vector("is_host", n_boats)

    # visits[p][b]: which boat b visits in period p (n_boats means no visit)
    visits = m.int_matrix("visits", n_periods, n_boats, 0, n_boats)

    # Constraint: non-hosts can visit, hosts stay
    for b in range(n_boats):
        for p in range(n_periods):
            m &= ((~is_host[b]) | (visits[p][b] == n_boats))

    # Constraint: cannot visit itself
    for b in range(n_boats):
        for p in range(n_periods):
            m &= (visits[p][b] != b)

    # Constraint: no revisits (guests cannot visit same host twice across all periods)
    counter = 0
    for guest in range(n_boats):
        for host in range(n_boats):
            if guest != host:
                # Create a unique counter to track visits
                visit_count = 0
                for p in range(n_periods):
                    # Use unique variable name for each (guest, host, period) combo
                    visit_bool = m.bool(f"visit_g{guest}_h{host}_p{p}")
                    m &= (visit_bool == (visits[p][guest] == host))
                    visit_count += visit_bool
                # At most one visit
                m &= (visit_count <= 1)

    # Constraint: capacity - for each period and host, total crew cannot exceed capacity
    for p in range(n_periods):
        for host in range(n_boats):
            total_crew = crew_size[host]
            for guest in range(n_boats):
                if guest != host:
                    # Use unique variable name for capacity check
                    is_visiting = m.bool(f"cap_p{p}_h{host}_g{guest}")
                    m &= (is_visiting == (visits[p][guest] == host))
                    total_crew += is_visiting * crew_size[guest]
            m &= (total_crew <= capacity[host])

    # Objective: minimize number of hosts
    num_hosts = m.sum_var(is_host)
    for k in range(1, n_boats + 1):
        m.obj[1] += (num_hosts >= k)

    return m, {"is_host": is_host, "visits": visits}
