% session1_bank_card: a clingo model from DCP Rosetta.
%
% My bank card has a 4-digit PIN abcd. No two digits are the same, the 2-digit number cd is 3 times the 2-digit number ab, and the 2-digit number da is 2 times the 2-digit number bc. Find the PIN.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_bank_card.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% each of the four digits a, b, c, d is one digit from 0 to 9
digit(0..9).
1 { a(D) : digit(D) } 1.
1 { b(D) : digit(D) } 1.
1 { c(D) : digit(D) } 1.
1 { d(D) : digit(D) } 1.

% no two digits are the same
pin(a,D) :- a(D).
pin(b,D) :- b(D).
pin(c,D) :- c(D).
pin(d,D) :- d(D).
:- pin(X,D), pin(Y,D), X < Y.

% the 2-digit number cd is 3 times the 2-digit number ab
:- a(A), b(B), c(C), d(D), 10*C + D != 3*(10*A + B).

% the 2-digit number da is 2 times the 2-digit number bc
:- a(A), b(B), c(C), d(D), 10*D + A != 2*(10*B + C).

#show a/1.
#show b/1.
#show c/1.
#show d/1.
