% cur_num: a clingo model from DCP Rosetta.
%
% The number 48 has this peculiarity: if you add 1 to it the result is a square number, and if you add 1
% to its half you also get a square number. Find another number with this peculiarity, between 1 and 10000.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/cur_num.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% the candidates are the numbers 1 to the limit, and the squares needed are those up to limit+1
limit(10000).
candidate(1..L) :- limit(L).
square(R*R) :- limit(L), R = 1..L, R*R <= L+1.

% exactly one number other than 48 is chosen
1 { peculiar(N) : candidate(N), N != 48 } 1.

% if you add 1 to it, the result is a square number
:- peculiar(N), not square(N+1).

% its half is a whole number, and adding 1 to the half gives a square number
:- peculiar(N), N \ 2 != 0.
:- peculiar(N), not square(N/2+1).

#show peculiar/1.
