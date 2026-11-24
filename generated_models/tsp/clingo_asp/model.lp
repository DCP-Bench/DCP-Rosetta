% tsp: a clingo model from DCP Rosetta.
%
% The travelling salesman problem asks: given a list of cities and the distances between each pair of cities (or the
% locations of the cities), what is the shortest possible route that visits each city exactly once and returns to the
% origin city? The distance is the Euclidean distance between the points, rounded to an integer.
%
% Save this file as model.lp. Download `tsp.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/tsp.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py tsp.json
%   python -m clingo model.lp tsp_1.lp
%
% Input: locations(I, 0, X) and locations(I, 1, Y): the x and y coordinates of city I (0-based).

city(I) :- locations(I, 0, _).

% For two different cities, S is the sum of the absolute differences of their coordinates and Q the sum of the
% squares of those differences (the squared Euclidean distance).
pair(I, J, S, Q) :-
    locations(I, 0, X1), locations(I, 1, Y1), locations(J, 0, X2), locations(J, 1, Y2), I != J,
    S = |X1 - X2| + |Y1 - Y2|, Q = (X1 - X2) * (X1 - X2) + (Y1 - Y2) * (Y1 - Y2).

% The rounded distance D of a pair: the root of Q lies between S/2 and S, and it rounds to D exactly when
% D*(D-1) < Q <= D*(D+1). Clingo has no square root, so D is found this way. Identical points are at distance 0.
dist(I, J, 0) :- pair(I, J, _, 0).
dist(I, J, D) :- pair(I, J, S, Q), Q > 0, D = S / 2..S, D * (D - 1) < Q, Q <= D * (D + 1).

% each city is left by exactly one leg and entered by exactly one leg
1 { successor(I, J) : city(J), I != J } 1 :- city(I).
1 { successor(I, J) : city(I), I != J } 1 :- city(J).

% the legs form one single round trip through all the cities: starting from city 0 and following the legs
% reaches every city, so there are no separate loops
reached(0).
reached(J) :- reached(I), successor(I, J).
:- city(J), not reached(J).

% the length of the route is as short as possible: the sum of the distances of the legs travelled
#minimize { D, I, J : successor(I, J), dist(I, J, D) }.

% travel_distance is the length of the optimal route
travel_distance(C) :- C = #sum { D, I, J : successor(I, J), dist(I, J, D) }.

#show travel_distance/1.
