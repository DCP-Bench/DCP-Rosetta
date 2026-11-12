% best_host: a clingo model from DCP Rosetta.
%
% Six guests sit around a dinner table with six seats, and some guests do not get along with each other. If two guests who do not get along are seated next to each other, it creates conflict at dinner. Arrange the guests in a seating order that minimizes conflict. Andrew will only sit next to Dave and Frank; Betty will only sit next to Cara and Erica; Cara will only sit next to Betty and Frank; Dave will only sit next to Andrew and Erica; Erica will only sit next to Betty and Dave; Frank will only sit next to Andrew and Cara. An arrangement without any conflict exists, so every guest must sit only next to the two guests they will sit next to.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/best_host.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% the guests, numbered 0 to 5: 0 Andrew, 1 Betty, 2 Cara, 3 Dave, 4 Erica, 5 Frank
guest(0..5).

% the seats around the table, numbered 0 to 5 in the seating order
seat(0..5).

% the seats next to each other, in both directions (the table is round)
adjacent(P, (P+1)\6) :- seat(P).
adjacent(Q, P) :- adjacent(P, Q).

% the guests each guest will sit next to, in both directions
sits_next(0,3). sits_next(0,5). sits_next(1,2). sits_next(1,4). sits_next(2,1). sits_next(2,5).
sits_next(3,0). sits_next(3,4). sits_next(4,1). sits_next(4,3). sits_next(5,0). sits_next(5,2).

% each seat holds exactly one guest
1 { x(P, G) : guest(G) } 1 :- seat(P).

% each guest sits in exactly one seat
1 { x(P, G) : seat(P) } 1 :- guest(G).

% two guests seated next to each other are ones who will sit next to each other
:- x(P, G), x(Q, H), adjacent(P, Q), not sits_next(G, H).

#show x/2.
