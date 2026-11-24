% pythagorean_triplet: a clingo model from DCP Rosetta.
%
% A Pythagorean triplet is a set of three natural numbers a, b and c for which a^2 + b^2 = c^2. The order of a and b does not matter. There exists exactly one Pythagorean triplet for which a + b + c = 1000.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/pythagorean_triplet.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% the required sum of the three numbers
#const total = 1000.

% a is the smallest of the three numbers (the order of a and b does not matter), so a < b < c and
% 3a < a + b + c = total
1 { a(A) : A = 1..(total-1)/3 } 1.

% Searching b and c as well grounds a large product, so b and c are derived from a: substituting
% c = total - a - b into a^2 + b^2 = c^2 gives 2 (total - a) b = total^2 - 2 total a, so
% b = (total^2 - 2 total a) / (2 (total - a)), which must be a whole number. b_of(A,B) and c_of(A,C)
% hold the b and c that go with a = A.
:- a(A), (total*total - 2*total*A) \ (2*(total - A)) != 0.
b_of(A,B) :- a(A), B = (total*total - 2*total*A) / (2*(total - A)).
c_of(A,C) :- a(A), b_of(A,B), C = total - A - B.

% b is larger than a, and c is larger than b
:- a(A), b_of(A,B), not A < B.
:- a(A), b_of(A,B), c_of(A,C), not B < C.

% a^2 + b^2 = c^2
:- a(A), b_of(A,B), c_of(A,C), A*A + B*B != C*C.

b(B) :- a(A), b_of(A,B).
c(C) :- a(A), c_of(A,C).

#show a/1.
#show b/1.
#show c/1.
