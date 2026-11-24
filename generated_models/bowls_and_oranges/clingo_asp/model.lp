% bowls_and_oranges: a clingo model from DCP Rosetta.
%
% You have a number of bowls, numbered from 1 and all placed in a line at exact intervals of 1 meter. You also have a number of oranges. You wish to place all the oranges in the bowls, no more than one orange in each bowl, so that there are no three oranges A, B, and C such that the distance between A and B is equal to the distance between B and C.
%
% Save this file as model.lp. Download `bowls_and_oranges.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/bowls_and_oranges.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py bowls_and_oranges.json
%   python -m clingo model.lp bowls_and_oranges_1.lp

% Input: n(N) holds the number N of bowls, numbered 1 to N; m(M) holds the number M of oranges.

bowl(1..N) :- n(N).

% each of the M oranges is in a different bowl
M { orange(B) : bowl(B) } M :- m(M).

% no three oranges A, B and C have the distance between A and B equal to the distance between B and C
:- orange(A), orange(B), orange(C), A < B, B < C, A + C = 2 * B.

% the position of each orange in ascending order is the number of oranges in the bowls before it
position(B, I) :- orange(B), I = #count { C : orange(C), C < B }.
x(I, B) :- position(B, I).

#show x/2.
