% fixed_charge: a clingo model from DCP Rosetta.
%
% A company manufactures shirts, shorts, and pants. Each product requires a number of hours of labor and a certain amount of cloth, and the company has a limited capacity of both. In addition, all of these products can be manufactured only by renting an appropriate machine, each product having its own machine type. The renting cost of a machine is paid once, however much is made on it. The profit on the products (excluding the cost of renting the equipment) is also known, per unit, and each product is made in a whole number of units. The company would like to maximize its profit: the profit on the units made, less the cost of the machines rented.
%
% Save this file as model.lp. Download `fixed_charge.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/fixed_charge.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py fixed_charge.json
%   python -m clingo model.lp fixed_charge_1.lp

% Input: shirt(P), shorts(P), pants(P) hold the index P of each product; shirtM(M), shortM(M), pantM(M)
% hold the index M of the machine type each product needs; renting_cost(M, C) holds the renting cost C of
% machine M; product(P, 0, V) holds the profit V per unit of product P (the other column is not used);
% use(P, R, U) holds the amount U of resource R (0 labor, 1 cloth) per unit of product P; capacity(R, C)
% holds the capacity C of resource R; max_production(B) holds the largest number B of units of one product.

% the products are those that have a profit per unit
prod(P) :- product(P, 0, _).

% the machine type each product needs
machine_of(P, M) :- shirt(P), shirtM(M).
machine_of(P, M) :- shorts(P), shortM(M).
machine_of(P, M) :- pants(P), pantM(M).

% the profit per unit of each product
profit(P, V) :- product(P, 0, V).

% the number of units made of each product is between 0 and the largest production
1 { made(P, X) : X = 0..B } 1 :- prod(P), max_production(B).

% a machine is rented when a product that needs it is made
rented(M) :- machine_of(P, M), made(P, X), X > 0.

% the labor and cloth used by the units made do not exceed the capacity of each resource
:- capacity(R, C), #sum { U*X, P : made(P, X), use(P, R, U) } > C.

% the total profit less the renting cost of the machines rented, which is to be maximized
#maximize { V*X, product, P : made(P, X), profit(P, V); -C, machine, M : rented(M), renting_cost(M, C) }.

% the bounds of the value z: the largest profit when every product is made at the largest production,
% and the largest renting cost paid, which is the sum of all the machines' renting costs
top(S) :- S = #sum { V*B, P : profit(P, V), max_production(B) }.
bottom(-R) :- R = #sum { C, M : renting_cost(M, C) }.

% z is the maximum profit: it is the total profit less the renting cost of the machines rented. The bounded
% choice and check constraint below are an encoding chosen on purpose: writing z as one #sum assignment over
% the choice atoms exhausts grounding (timeouts).
1 { z(Z) : Z = L..T } 1 :- bottom(L), top(T).
:- z(Z), Z != #sum { V*X, product, P : made(P, X), profit(P, V); -C, machine, M : rented(M), renting_cost(M, C) }.

#show z/1.
