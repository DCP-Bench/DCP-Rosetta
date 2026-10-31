Blind model. A first draft with exact difference binaries (one-hot difference per (lag, i), an
equation tying it to X, and channelling rows in both directions) took 153 s on n=8 and timed out
on n=9..12. Dropping the equation and keeping only the rows that push a continuous indicator to 1
when X_i = v and X_{i+l} = v + d (with at most one indicator per lag and difference) solved
n=8..11 in 3-59 s. n=12 (json:4) found one array but not a second within 180 s: an
execution_timeout skip, 4 of 5 instances checked, a performance limit of CBC on this encoding.
