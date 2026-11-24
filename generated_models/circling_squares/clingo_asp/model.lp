% circling_squares: a clingo model from DCP Rosetta.
%
% Circling the squares: the puzzle is to place a different number in each of the ten squares so that the sum of
% the squares of any two adjacent numbers shall be equal to the sum of the squares of the two numbers
% diametrically opposite to them. The numbers placed, as examples, must stand as they are: A=16, B=2, F=8 and
% G=14. In the same way, B and C should be equal to G and H, A and K to F and E, H and I to C and D, and so on,
% with any two adjoining squares in the circle. The numbers are whole numbers, fractions are not allowed, and no
% number need contain more than two figures.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/circling_squares.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% the squares of the circle, in order: a, b, c, d, e, f, g, h, i, k
square(a;b;c;d;e;f;g;h;i;k).

% value(S, V): the square S holds the number V, a whole number from 1 to 99
1 { value(S, V) : V = 1..99 } 1 :- square(S).

% the numbers in the squares are all different
:- value(S, V), value(T, V), S < T.

% the given numbers
given(a, 16). given(b, 2). given(f, 8). given(g, 14).
:- given(S, V), not value(S, V).

% equal_pairs(P, Q, R, S): the squares of the numbers in the adjacent squares P and Q add up to the squares of
% the numbers in the squares R and S, which are opposite them
equal_pairs(a, b, f, g).
equal_pairs(b, c, g, h).
equal_pairs(c, d, h, i).
equal_pairs(d, e, i, k).
equal_pairs(e, f, k, a).

% the sum of the squares of P and Q minus the sum of the squares of R and S is zero
:- equal_pairs(P, Q, R, S),
   #sum { V*V,P : value(P, V); V*V,Q : value(Q, V); -V*V,R : value(R, V); -V*V,S : value(S, V) } != 0.

% one atom per square: a(V) says that the square a holds the number V, and so on
a(V) :- value(a, V).
b(V) :- value(b, V).
c(V) :- value(c, V).
d(V) :- value(d, V).
e(V) :- value(e, V).
f(V) :- value(f, V).
g(V) :- value(g, V).
h(V) :- value(h, V).
i(V) :- value(i, V).
k(V) :- value(k, V).

#show a/1.
#show b/1.
#show c/1.
#show d/1.
#show e/1.
#show f/1.
#show g/1.
#show h/1.
#show i/1.
#show k/1.
