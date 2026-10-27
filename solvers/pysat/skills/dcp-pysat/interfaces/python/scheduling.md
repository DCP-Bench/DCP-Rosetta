# PySAT scheduling at realistic size

Back to [the Python interface](README.md).

## Scheduling at realistic size

A reified no-overlap constraint over integer starts is quadratic in the horizon for every pair of tasks. Measured on ft06 (6 jobs, 6 machines, 15 reified pairs per machine), clause counts from `engine.clausify()`:

| Horizon | Start encoding | Hard clauses | Clausify time |
|---|---|---|---|
| 197 (sum of durations) | `order` | 13.6M | 21 s |
| 197 | `direct` | 11.9M | 19 s |
| 80 | `order` starts, `coupled` makespan | 1.16M | 1.4 s |
| 68 (greedy schedule) | `order` starts, `coupled` makespan | 0.64M | 0.7 s |
| 55 (optimum) | `direct` | 0.23M | 0.3 s |

Three rules follow:

1. **Horizon:** use the makespan of any feasible schedule, such as a greedy list schedule that always starts the operation that can begin earliest. The sum of durations is a valid horizon but the worst one.
2. **Start domains:** a task's lower bound is the sum of durations before it in its job (its head); its upper bound is `horizon - tail - duration`, where the tail is the sum after it. Without these bounds the same 197 run had 18.2M clauses.
3. **Encoding:** at the same horizon, `direct` starts gave about 13 % fewer clauses than `order`. The horizon is the lever, not the encoding.

With the greedy horizon and unit-weight threshold softs, ft06 solves to the optimum 55 in about 3 s on one CPU: [assets/jobshop](../../assets/python/jobshop/README.md). Skip a reified selector that comes back `None`, and check the schedule independently after decoding. In a measured run, weighted makespan softs with distinct weights at horizon 197 took about 110 s of RC2 time.

