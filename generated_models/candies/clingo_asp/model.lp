% candies: a clingo model from DCP Rosetta.
%
% Alice is a kindergarten teacher. The children sit in a line, and each has a rating score according to
% their usual performance. Alice gives at least 1 candy to each child. If two children sit next to each
% other, the one with the higher rating must get more candies than the other. Alice wants to save money,
% so she wants to minimize the total number of candies.
%
% Save this file as model.lp. Download `candies.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/candies.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py candies.json
%   python -m clingo model.lp candies_1.lp

% Input: ratings(I, R): child I (numbered from 0 along the line) has the rating R.

child(I) :- ratings(I, _).
children(N) :- N = #count { I : child(I) }.

% each child gets at least one candy; no child needs more candies than there are children,
% so the number of candies of a child is at most the number of children
1 { x(I, 1..N) } 1 :- child(I), children(N).

% of two neighbours, the child with the higher rating gets more candies (equal ratings are not compared)
:- ratings(I, R1), ratings(I + 1, R2), R1 > R2, x(I, C1), x(I + 1, C2), C1 <= C2.
:- ratings(I, R1), ratings(I + 1, R2), R1 < R2, x(I, C1), x(I + 1, C2), C1 >= C2.

% z: the total number of candies, which is as small as possible
z(Z) :- Z = #sum { C, I : x(I, C) }.
#minimize { Z : z(Z) }.

#show x/2.
#show z/1.
