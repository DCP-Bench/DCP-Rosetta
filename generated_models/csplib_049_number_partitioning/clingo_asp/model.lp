% csplib_049_number_partitioning: a clingo model from DCP Rosetta.
%
% This problem consists of finding a partition of numbers 1..N into two sets A and B such that:
%
% - A and B have the same cardinality
% - Sum of numbers in A = sum of numbers in B
% - Sum of squares of numbers in A = sum of squares of numbers in B
%
% Save this file as model.lp. Download `csplib_049_number_partitioning.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_049_number_partitioning.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_049_number_partitioning.json
%   python -m clingo model.lp csplib_049_number_partitioning_1.lp

% Input: n(N): the largest number N, so the numbers to partition are 1..N.

num(1..N) :- n(N).

% each number is in A or in B, but not in both
{ in_a(X) : num(X) }.
in_b(X) :- num(X), not in_a(X).

% the cardinalities, sums and sums of squares of A and B
card_a(N) :- N = #count { X : in_a(X) }.
card_b(N) :- N = #count { X : in_b(X) }.
sum_a(S) :- S = #sum { X,X : in_a(X) }.
sum_b(S) :- S = #sum { X,X : in_b(X) }.
squares_a(S) :- S = #sum { X*X,X : in_a(X) }.
squares_b(S) :- S = #sum { X*X,X : in_b(X) }.

% A and B have the same cardinality
:- card_a(N), card_b(M), N != M.

% the sums of the numbers in A and in B are equal
:- sum_a(S), sum_b(T), S != T.

% the sums of the squares of the numbers in A and in B are equal
:- squares_a(S), squares_b(T), S != T.

% the members of A and B, listed in increasing order with their 0-based positions
a(I,X) :- in_a(X), I = #count { Y : in_a(Y), Y < X }.
b(I,X) :- in_b(X), I = #count { Y : in_b(Y), Y < X }.

#show a/2.
#show b/2.
