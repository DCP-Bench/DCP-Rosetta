% giant_cat_army: a clingo model from DCP Rosetta.
%
% Basically you start with [0], then you build this list by using one of three operations: adding 5, adding 7,
% or taking sqrt. You successfully complete the game when you have managed to build a list such that 2, 10 and
% 14 appear on the list, in that order, and there can be other numbers between them. The rules also require
% that all the elements are distinct, they are all at most 60 and are all integers. The list starts with 0,
% ends with 14, and has a length of 24.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/giant_cat_army.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% the list has 24 numbers, at positions 0 to 23, and the numbers are 0 to 60
length(24).
index(0..L-1) :- length(L).
value(0..60).

% x(I, V): the I-th number of the list is V
1 { x(I, V) : value(V) } 1 :- index(I).

% all the numbers are different
:- x(I, V), x(J, V), I < J.

% the list starts with 0 and ends with 14
:- not x(0, 0).
:- length(L), not x(L - 1, 14).

% from each number the next one is reached by adding 5, by adding 7, or by taking the square root
% (step(V, W): W follows V)
step(V, V + 5) :- value(V), value(V + 5).
step(V, V + 7) :- value(V), value(V + 7).
step(V * V, V) :- value(V), value(V * V).
:- x(I, V), x(I + 1, W), not step(V, W).

% the list contains 10 and 2, and 2 comes before 10 (14 is last, so 10 comes before 14)
:- not 1 { x(I, 10) : index(I) }.
:- not 1 { x(I, 2) : index(I) }.
:- x(J, 10), #count { I : x(I, 2), I < J } < 1.

#show x/2.
