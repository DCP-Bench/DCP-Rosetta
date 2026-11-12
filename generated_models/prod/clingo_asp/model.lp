% prod: a clingo model from DCP Rosetta.
%
% Consider a problem where we have a set `P`. For each element `j` in `P`, we have a parameter `a[j]`, a parameter `c[j]`, and a parameter `u[j]`. We also have a global parameter `b`. We have a variable `X[j]` for each `j` in `P`. The goal is to maximize the total profit, which is the sum of `c[j] * X[j]` for all `j` in `P`. The constraints are that the sum of `(1/a[j]) * X[j]` for all `j` in `P` should be less than or equal to `b`, and `X[j]` should be between 0 and `u[j]` for all `j` in `P`.
%
% Save this file as model.lp. Download `prod.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/prod.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py prod.json
%   python -m clingo model.lp prod_1.lp
%
% Input: a(J, A) the parameter a of element J; c(J, C) the parameter c of element J; u(J, U) the parameter u of
% element J; b(B) the global parameter b (indices are 0-based, as in the data).

product(J) :- a(J,_).

% x(J,V): X[J] takes the value V, between 0 and u[J]
1 { x(J,V) : V = 0..U } 1 :- product(J), u(J,U).

% The fractions 1/a[j] are made whole numbers by multiplying the capacity constraint by P, the product
% of all the a[j]: P/a[j] is then a whole number. scale(J,P) is the product of a[0..J-1].
scale(0,1).
scale(J+1,P*A) :- scale(J,P), a(J,A).
common(P) :- scale(N,P), N = #count { J : product(J) }.

% the sum of (1/a[j]) * X[j] is at most b (multiplied by P on both sides)
:- common(P), b(B), #sum { (P/A)*V,J : x(J,V), a(J,A) } > B*P.

% total_profit: the sum of c[j] * X[j] over all elements
total_profit(S) :- S = #sum { C*V,J : x(J,V), c(J,C) }.

% the total profit is as large as possible
#maximize { C*V,J : x(J,V), c(J,C) }.

#show x/2.
#show total_profit/1.
