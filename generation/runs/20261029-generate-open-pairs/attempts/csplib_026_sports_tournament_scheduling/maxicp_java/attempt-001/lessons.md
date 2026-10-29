Blind model. Earlier attempts (20261016-maxicp-java-models) timed out on 8 teams with Boolean
and slot-permutation encodings. This one: home/away team variables per week and period, a table
to an unordered game id with allDifferent over the real weeks, allDifferent per week, and Regin's
dummy week so every team plays exactly twice in every period (any tournament extends to it, so
no solution is lost). Without anything else 8 teams still timed out in 120 s. The decisive change
is one registered Boolean per slot equal to [home > away], registered first: no rule depends on
which team of a game is at home, so firstFailBinary fixes those flags at the top and never
re-explores a failed set of games under the other orientation. 8 teams then takes about 2 s.
Teams are numbered 1..n as the description says; the evaluator accepted that numbering.
