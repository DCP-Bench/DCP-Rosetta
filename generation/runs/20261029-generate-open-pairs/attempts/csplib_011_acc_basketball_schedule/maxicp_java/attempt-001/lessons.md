Blind model, first try accepted. Earlier attempts in 20261016-maxicp-java-models timed out with
Boolean or opponent-first encodings. This one decides per mirrored round (9 rounds, the pairs of
dates in the mirroring scheme): a venue variable per team (domain 3, registered first, so
firstFailBinary fixes the home/away/bye pattern before the opponents) and an opponent variable
per team that is an involution of the round (element(opp, opp[i]) = i, self for the bye). The
mirror date's venue is a view (2 - venue). It finds two schedules in about 2 s. Conventions that
the evaluator accepted: teams 0-based in the statement's order, a bye written as the team itself
in config. Constraint 8 is read strictly (either order for UNC/Duke, any order for the three).
Single instance: the model takes n_teams and n_days from the instance, but the team names, the
mirroring scheme and the dated rules are fixed by the statement.
