% four_islands: a clingo model from DCP Rosetta.
%
% A tiny nation in the South Pacific contains four islands connected by bridges as shown. Each of the four
% islands (Pwana, Quero, Rayou, and Skern) boasts a different primary export (alabaster, bananas, coconuts,
% and durian fruit) and a different tourist attraction (hotel, ice skating rink, jai alai stadium, and koala
% preserve). Find the name, export, and tourist attraction of each island on the map.
%
% The islands A, B, C, D are laid out as
%   (A) -- (B)
%    |      |
%   (C) -- (D)
% so A is north of C, C is west of D, etc.
%
% 1. The island noted for its koala preserve is due south of Pwana.
% 2. The island with the largest alabaster quarry is due west of Quero.
% 3. The island with the resort hotel is due east of the one that exports durian fruit.
% 4. Skern and the island with the jai alai stadium are connected by a north-south bridge.
% 5. Rayou and the island that exports bananas are connected by an east-west bridge.
% 6. The islands noted for the South Pacific's largest ice skating rink and for the jai alai stadium are
%    not connected by a bridge.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/four_islands.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp
%
% The map positions are A=0, B=1, C=2, D=3. island(I, S): the island I is at spot S, with I = 0 Pwana,
% 1 Quero, 2 Rayou, 3 Skern. export(E, S): the island at spot S exports E, with E = 0 alabaster, 1 bananas,
% 2 coconuts, 3 durian fruit. attraction(T, S): the island at spot S has attraction T, with T = 0 resort
% hotel, 1 ice skating rink, 2 jai alai stadium, 3 koala preserve.

spot(0..3).
idx(0..3).

% each island, export and attraction is at exactly one spot, and each spot holds exactly one of each
1 { island(I, S) : spot(S) } 1 :- idx(I).
1 { export(E, S) : spot(S) } 1 :- idx(E).
1 { attraction(T, S) : spot(S) } 1 :- idx(T).
:- island(I, S), island(J, S), I < J.
:- export(E, S), export(F, S), E < F.
:- attraction(T, S), attraction(U, S), T < U.

% the map: north(X, Y) means spot X is due north of spot Y, and west(X, Y) that spot X is due west of spot Y
north(0, 2). north(1, 3).
west(0, 1). west(2, 3).

% the other directions follow from these
south(X, Y) :- north(Y, X).
east(X, Y) :- west(Y, X).

% two spots are joined by a bridge when they lie north and south of each other, or west and east of each other
bridge(X, Y) :- north(X, Y).
bridge(X, Y) :- north(Y, X).
bridge(X, Y) :- west(X, Y).
bridge(X, Y) :- west(Y, X).
apart(X, Y) :- spot(X), spot(Y), X != Y, not bridge(X, Y).

% 1. the koala preserve is due south of Pwana
:- island(0, P), attraction(3, K), not south(K, P).

% 2. the alabaster quarry is due west of Quero
:- export(0, A), island(1, Q), not west(A, Q).

% 3. the resort hotel is due east of the durian fruit exporter
:- export(3, D), attraction(0, H), not east(H, D).

% 4. Skern and the jai alai stadium are connected by a north-south bridge
:- island(3, S), attraction(2, J), not north(S, J), not north(J, S).

% 5. Rayou and the banana exporter are connected by an east-west bridge
:- island(2, R), export(1, B), not west(R, B), not west(B, R).

% 6. the ice skating rink and the jai alai stadium are not connected by a bridge
:- attraction(1, I), attraction(2, J), not apart(I, J).

#show island/2.
#show export/2.
#show attraction/2.
