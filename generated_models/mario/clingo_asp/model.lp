% mario: a clingo model from DCP Rosetta.
%
% Mario needs to collect as much gold as possible by visiting different houses. He starts at Mario's house and ends at Luigi's house. Each house has a certain amount of gold and the travel between houses consumes fuel. Mario has a limited amount of fuel, and he needs to plan his route to maximize the gold collected without exceeding the fuel limit.
%
% Save this file as model.lp. Download `mario.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/mario.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py mario.json
%   python -m clingo model.lp mario_1.lp
%
% Input: nHouses(N) the number of houses; marioHouse(M), luigiHouse(L) the houses of Mario and Luigi; fuelLimit(F) the fuel Mario has; arc_fuel(I,J,C) the fuel C of travel from I to J; goldInHouse(I,G) the gold G in house I (0-based).

house(0..N-1) :- nHouses(N).

% s(I,J): the house succeeding house I is house J; J = I when house I is not on the route.
% Each house has exactly one succeeding house, and each house succeeds exactly one house.
1 { s(I,J) : house(J) } 1 :- house(I).
1 { s(I,J) : house(I) } 1 :- house(J).

% the route ends at Luigi's house, from which it goes back to Mario's house
:- luigiHouse(L), marioHouse(M), not s(L,M).

% on_route(I): house I is on the route, which starts at Mario's house and follows the successors up to Luigi's house
on_route(M) :- marioHouse(M).
on_route(J) :- on_route(I), s(I,J), luigiHouse(L), I != L.

% every house that is not its own successor is on the route, so no separate loop of houses is formed
:- s(I,J), I != J, not on_route(I).

% the fuel burned on the travel from Mario's house to Luigi's house stays within the fuel limit
% (the return from Luigi's house to Mario's house is not travel of the route)
:- fuelLimit(F), luigiHouse(L), #sum { C,I : s(I,J), I != J, I != L, arc_fuel(I,J,C) } > F.

% maximize the gold in the houses on the route
#maximize { G,I : s(I,J), I != J, goldInHouse(I,G) }.

#show s/2.
