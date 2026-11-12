% session3_people_in_a_room: a clingo model from DCP Rosetta.
%
% There are 13 people. 4 of them are male. They randomly enter a room one at a time. Find a way that the males and females enter so that the ratio of females to males in the room at any one time is no greater than 7/3?
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_people_in_a_room.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% the 13 people enter in the positions 0 to 12, in order
position(0..12).

% 4 of the people entering are male; each of the others is female
{ male(P) : position(P) } = 4.
female(P) :- position(P), not male(P).

% the number of females and of males in the room after each entrance
females_in_room(T, F) :- position(T), F = #count { P : female(P), P <= T }.
males_in_room(T, M)   :- position(T), M = #count { P : male(P), P <= T }.

% at any time the ratio of females to males in the room is no greater than 7/3, i.e. 3 * females <= 7 * males
:- females_in_room(T, F), males_in_room(T, M), 3 * F > 7 * M.

% the output: true for each female entrance (1) and false for each male entrance (0)
sequence(P, true)  :- female(P).
sequence(P, false) :- male(P).

#show sequence/2.
