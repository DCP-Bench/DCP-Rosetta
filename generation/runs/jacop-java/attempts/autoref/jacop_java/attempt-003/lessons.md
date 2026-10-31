hints.md (coordinator's notes) was used for this retry.

Attempt 002 used `Count(s, s[i], i)`, where the counter is also an element of the counted list. JaCoP
then emitted a wrong first solution on the n=3, m=0 instance and the right one second. `GCC(s, counters)`
with counters = s[0..n] fixes it (GCC counts the values 0, 1, ... in order). Always check the first
solution the runner emits, not a later one.
