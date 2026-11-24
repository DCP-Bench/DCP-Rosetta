% session5_hardy_1729_square: a clingo model from DCP Rosetta.
%
% Find a combination of 4 different numbers between 1 and 100, such that the sum of the squares of the two first numbers is equal to the sum of the squares of the other two numbers, i.e. a^2 + b^2 = c^2 + d^2 for a, b, c and d between 1 and 100, all different.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_hardy_1729_square.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

num(1..100).

% each of a, b, c and d is one of the numbers from 1 to 100
1 { a(V) : num(V) } 1.
1 { b(V) : num(V) } 1.
1 { c(V) : num(V) } 1.
1 { d(V) : num(V) } 1.

% the four numbers are all different
:- a(X), b(X).
:- a(X), c(X).
:- a(X), d(X).
:- b(X), c(X).
:- b(X), d(X).
:- c(X), d(X).

% the sum of the squares of a and b is equal to the sum of the squares of c and d
:- #sum { A*A, a : a(A) ; B*B, b : b(B) ; -(C*C), c : c(C) ; -(D*D), d : d(D) } != 0.

#show a/1.
#show b/1.
#show c/1.
#show d/1.
