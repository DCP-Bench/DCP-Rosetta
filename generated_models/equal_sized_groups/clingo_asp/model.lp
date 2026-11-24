% equal_sized_groups: a clingo model from DCP Rosetta.
%
% I have a sorted list of N elements, and I want to divide them into K groups, by choosing K-1 split points between them. There may be elements with the same value, and it is necessary to have items with same value in the same group. Find K groups as close in size to round(N/K) as possible. Each group holds at least one element.
%
% Save this file as model.lp. Download `equal_sized_groups.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/equal_sized_groups.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py equal_sized_groups.json
%   python -m clingo model.lp equal_sized_groups_1.lp

% Input: a(I, V) holds the value V of the I-th element of the sorted list (indices 0-based);
% k(K) holds the number K of groups.

% the elements are those that have a value, and N is their number
element(I) :- a(I, _).
n(N) :- N = #count { I : element(I) }.

% the split points are the positions 1..N-1: a split point P puts elements 0..P-1 before it
step(1..N-1) :- n(N).

% choose exactly K-1 split points
{ cut(P) : step(P) } = K-1 :- k(K).

% a split point cannot separate two items with the same value
:- cut(P), a(P-1, V), a(P, V).

% before(P, I): I split points lie before position P
before(1, 0).
before(P+1, I+1) :- before(P, I), cut(P).
before(P+1, I) :- before(P, I), step(P), not cut(P).

% the split points in order: x(I, P) is the I-th split point (0-based) at position P
x(I, P) :- cut(P), before(P, I).

% target size of each group: round(N/K), rounding halves up
target(T) :- n(N), k(K), T = (2*N + K) / (2*K).

% last(P, S): the last split point before position P is at S (0 if there is none)
last(1, 0) :- n(_).
last(P+1, P) :- cut(P).
last(P+1, S) :- last(P, S), step(P), not cut(P).

% the error of each group ending at a split point E, and starting at the split point S: |size - round(N/K)|
% the last group ends at N
#minimize { |E - S - T|, S, E : cut(E), last(E, S), target(T) }.
#minimize { |N - S - T|, S, end : n(N), last(N, S), target(T) }.

#show x/2.
