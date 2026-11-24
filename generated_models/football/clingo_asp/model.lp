% football: a clingo model from DCP Rosetta.
%
% Statistics show that, in the Premiership, there is a strong correlation between the value of a team's
% players and their final position in that league - so you want to spend as much money as you can. The
% chairman gives you an upper limit of GBP 30 million - so you want your purchases to add up to as close
% to that figure as possible (without going over). You must buy exactly one goalkeeper, at least two
% defenders, at least three midfielders and at least two strikers, and at least eleven players in total.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/football.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% the players on offer: player(Name, Position, Price), with the price in GBP thousands
player(g1, goalkeeper, 730).   player(g2, goalkeeper, 1280).  player(g3, goalkeeper, 3880).
player(d1, defender, 920).     player(d2, defender, 1310).    player(d3, defender, 1620).
player(d4, defender, 2410).    player(d5, defender, 2790).    player(d6, defender, 3280).
player(d7, defender, 3910).    player(d8, defender, 4570).
player(m1, midfielder, 1800).  player(m2, midfielder, 2630).  player(m3, midfielder, 3170).
player(m4, midfielder, 3769).  player(m5, midfielder, 4140).  player(m6, midfielder, 4750).
player(m7, midfielder, 5380).  player(m8, midfielder, 5930).  player(m9, midfielder, 6780).
player(m10, midfielder, 7130).
player(s1, striker, 4460).     player(s2, striker, 6470).     player(s3, striker, 7780).
player(s4, striker, 8390).     player(s5, striker, 9500).

% the budget in GBP thousands, and the numbers of players to buy in each position
budget(30000).
min_total(11).
exactly(goalkeeper, 1).
at_least(defender, 2).
at_least(midfielder, 3).
at_least(striker, 2).

% buy(P): player P is bought
{ buy(P) : player(P, _, _) }.

% the number of players bought in a position is exactly (or at least) the number required
:- exactly(Pos, N), #count { P : buy(P), player(P, Pos, _) } != N.
:- at_least(Pos, N), #count { P : buy(P), player(P, Pos, _) } < N.

% at least eleven players are bought in total
:- min_total(N), #count { P : buy(P) } < N.

% the total price of the players bought is within the budget
:- budget(B), #sum { Pr, P : buy(P), player(P, _, Pr) } > B.

% z(S): the total price of the players bought is S, in GBP thousands
z(S) :- S = #sum { Pr, P : buy(P), player(P, _, Pr) }.

% the total price is as large as possible
#maximize { S : z(S) }.

% which players are bought is not part of the answer, so solutions are projected onto z
#project z/1.
#show z/1.
