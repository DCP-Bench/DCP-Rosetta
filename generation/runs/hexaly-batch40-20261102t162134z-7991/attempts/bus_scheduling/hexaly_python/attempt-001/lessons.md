# bus_scheduling attempt-001

Rejected on the example ("Declared outputs cannot extend to a reference solution"): the model
tied the demand of slot i to the buses starting in slots i and i + 1. After this failure the
reference was read: it covers slot i + 1 with those buses. Attempt-002 follows that reading.
