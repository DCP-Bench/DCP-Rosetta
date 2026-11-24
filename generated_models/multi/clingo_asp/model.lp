% multi: a clingo model from DCP Rosetta.
%
% This is a multi-commodity transportation problem. Given a set of origins `Origins`, a set of destinations `Destinations`, and a set of products `Products`. Each origin `i` has a certain supply of each product `p` `Supply_{i,p}` and each destination `j` has a certain demand for each product `p` `Demand_{j,p}`. The cost of shipping one unit of product `p` from origin `i` to destination `j` is `ShippingCost_{i, j, p}`. The problem aims to minimize the total cost of shipping all products from the origins to the destinations.
%
% Save this file as model.lp. Download `multi.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/multi.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py multi.json
%   python -m clingo model.lp multi_1.lp
%
% Input: supply(I, P, S) the supply S of product P at origin I; demand(J, P, D) the demand D of product P at
% destination J; limit(I, J, L) the most units L that can be shipped from origin I to destination J in total;
% cost(I, J, P, C) the cost C of shipping one unit of product P from origin I to destination J (0-based indices).

% the most units of product P that can be shipped from origin I to destination J
bound(I,J,P,B) :- supply(I,P,S), limit(I,J,L), B = #min { S ; L }.

% amount(I,J,P,A): A units of product P are shipped from origin I to destination J
1 { amount(I,J,P,A) : A = 0..B } 1 :- bound(I,J,P,B).

% the units of product P shipped out of origin I do not exceed its supply
:- supply(I,P,S), #sum { A,J : amount(I,J,P,A) } > S.

% the units of product P shipped to destination J meet its demand
:- demand(J,P,D), #sum { A,I : amount(I,J,P,A) } < D.

% the units of all products shipped from origin I to destination J stay within the limit (the instance's limit data; the description does not mention it)
:- limit(I,J,L), #sum { A,P : amount(I,J,P,A) } > L.

% total_cost: the shipping cost of all the units shipped
total_cost(T) :- T = #sum { A*C,I,J,P : amount(I,J,P,A), cost(I,J,P,C) }.

% the total shipping cost is as small as possible
#minimize { A*C,I,J,P : amount(I,J,P,A), cost(I,J,P,C) }.

#show total_cost/1.
