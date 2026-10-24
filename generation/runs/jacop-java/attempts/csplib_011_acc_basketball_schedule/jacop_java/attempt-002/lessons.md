# Lessons: csplib_011 on jacop_java

- Two attempts, both execution_timeout at 180 s on the single instance (no solution found).
- attempt-001: one Reified per (day, team, opponent) with a shared pair boolean, LinearInt for home/away
  channelling, mirroring as XeqY on config. Labelling config then where in input order.
- attempt-002: adds redundant counts (two byes per team, one weekday bye), labels mirror-representative
  dates first with SmallestDomain and IndomainMin. Still no solution in 180 s.
- Reading of the statement used: "away against UNC and Duke on consecutive dates" = one away game
  against each in either order; "three consecutive dates against UNC, Duke and Wake" = the three opponents
  in any order; bye encoded as config[d][i] == i; the mirroring scheme is applied to config, byes included.
  The config convention for a bye is not stated by the statement; check against the evaluator if a
  future attempt gets past the timeout.
- Not checked: whether the reference relies on conventions the statement leaves open.
