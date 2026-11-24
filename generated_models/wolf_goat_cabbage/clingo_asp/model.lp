% wolf_goat_cabbage: a clingo model from DCP Rosetta.
%
% The wolf, goat and cabbage problem is a river crossing puzzle. It dates back to at least the 9th century, and has
% entered the folklore of several cultures.
%
% The story: A farmer with a wolf, a goat, and a cabbage must cross a river by boat. The boat can carry only the farmer
% and a single item. If left unattended together, the wolf would eat the goat, or the goat would eat the cabbage. How can
% they cross the river without anything being eaten?
%
% The crossing takes the given number of stages. At the first stage everything is on the starting shore, at the last
% stage everything is on the destination shore, and the boat, with the farmer, changes shore from each stage to the next.
%
% Save this file as model.lp. Download `wolf_goat_cabbage.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/wolf_goat_cabbage.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py wolf_goat_cabbage.json
%   python -m clingo model.lp wolf_goat_cabbage_1.lp
%
% Input: stage(S) holds the number S of stages. A shore is 0 for the starting shore and 1 for the destination shore.

step(0..S - 1) :- stage(S).
last(S - 1) :- stage(S).

% at each stage the wolf, goat, cabbage and boat are each on one shore
1 { wolf_pos(T, P) : P = 0..1 } 1 :- step(T).
1 { goat_pos(T, P) : P = 0..1 } 1 :- step(T).
1 { cabbage_pos(T, P) : P = 0..1 } 1 :- step(T).
1 { boat_pos(T, P) : P = 0..1 } 1 :- step(T).

% at the first stage everything is on the starting shore
:- wolf_pos(0, 1).
:- goat_pos(0, 1).
:- cabbage_pos(0, 1).
:- boat_pos(0, 1).

% at the last stage everything is on the destination shore
:- last(T), wolf_pos(T, 0).
:- last(T), goat_pos(T, 0).
:- last(T), cabbage_pos(T, 0).
:- last(T), boat_pos(T, 0).

% the boat, with the farmer, changes shore from each stage to the next
:- boat_pos(T, P), boat_pos(T + 1, P), step(T + 1).

% the wolf, goat or cabbage can change shore only when the boat leaves from the shore it is on
:- wolf_pos(T, P), wolf_pos(T + 1, Q), P != Q, boat_pos(T, R), R != P.
:- goat_pos(T, P), goat_pos(T + 1, Q), P != Q, boat_pos(T, R), R != P.
:- cabbage_pos(T, P), cabbage_pos(T + 1, Q), P != Q, boat_pos(T, R), R != P.

% the boat carries the farmer and at most a single item
moving(T, wolf) :- wolf_pos(T, P), wolf_pos(T + 1, Q), P != Q.
moving(T, goat) :- goat_pos(T, P), goat_pos(T + 1, Q), P != Q.
moving(T, cabbage) :- cabbage_pos(T, P), cabbage_pos(T + 1, Q), P != Q.
:- step(T), #count { I : moving(T, I) } > 1.

% the wolf would eat the goat if they are on one shore, unattended by the farmer
:- wolf_pos(T, P), goat_pos(T, P), boat_pos(T, Q), Q != P.

% the goat would eat the cabbage if they are on one shore, unattended by the farmer
:- goat_pos(T, P), cabbage_pos(T, P), boat_pos(T, Q), Q != P.

#show wolf_pos/2.
#show goat_pos/2.
#show cabbage_pos/2.
#show boat_pos/2.
