% fixed_charge: a MiniZinc model from DCP Rosetta.
%
% A company manufactures shirts, shorts, and pants. Each product requires a number of hours of labor
% and a certain amount of cloth, and the company has a limited capacity of both. In addition, all of
% these products can be manufactured only by renting an appropriate machine, each product having its
% own machine type. The renting cost of a machine is paid once, however much is made on it. The
% profit on the products (excluding the cost of renting the equipment) is also known, per unit, and
% each product is made in a whole number of units. The company would like to maximize its profit:
% the profit on the units made, less the cost of the machines rented.
%
% Save this file as model.mzn. Download `fixed_charge.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/fixed_charge.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py fixed_charge.json
%   minizinc model.mzn fixed_charge_1.json

array[int] of int: capacity;                  % capacity[r]: the available amount of resource r
array[int] of int: renting_cost;              % renting_cost[m]: the cost of renting machine m
int: max_production;                          % the most units of one product that can be made
array[int, int] of int: product;              % product[p, 1]: profit per unit of product p
                                              % (column 2 repeats the product's own number)
array[int, int] of int: use;                  % use[p, r]: amount of resource r per unit of product p

set of int: Products = index_set_1of2(product);   % one index per product
set of int: Machines = index_set(renting_cost);   % one index per machine type
set of int: Resources = index_set(capacity);      % one index per resource

% produce[p]: units of product p made
array[Products] of var 0..max_production: produce;
% rent[m]: machine m is rented, which product p needs for its own machine type p
array[Machines] of var bool: rent;

% the labor and cloth used by the products made do not exceed the capacity of each
constraint forall(r in Resources)(sum(p in Products)(use[p, r] * produce[p]) <= capacity[r]);
% a product is made only when its machine is rented
constraint forall(p in Products)(produce[p] <= max_production * bool2int(rent[p]));

% the profit on the units made, less the cost of the machines rented
var int: objective = sum(p in Products)(product[p, 1] * produce[p])
    - sum(m in Machines)(renting_cost[m] * bool2int(rent[m]));

solve maximize objective;
output ["{\"z\": ", showJSON(objective), "}"];
