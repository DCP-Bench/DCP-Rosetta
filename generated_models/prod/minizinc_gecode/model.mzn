% prod: a MiniZinc model from DCP Rosetta.
%
% Consider a problem where we have a set P. For each element j in P, we have a parameter a[j], a
% parameter c[j], and a parameter u[j]. We also have a global parameter b. We have a variable X[j] for each
% j in P. The goal is to maximize the total profit, which is the sum of c[j] * X[j] for all j in P. The
% constraints are that the sum of (1/a[j]) * X[j] for all j in P should be less than or equal to b, and
% X[j] should be between 0 and u[j] for all j in P.
%
% Save this file as model.mzn. Download `prod.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/prod.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py prod.json
%   minizinc model.mzn prod_1.json

array[int] of int: a;                    % a[j]: the divisor of X[j] in the resource constraint
array[int] of int: c;                    % c[j]: the profit per unit of product j
array[int] of int: u;                    % u[j]: the upper bound on X[j]
int: b;                                  % the bound on the resource constraint

set of int: Products = index_set(a);

% X[j]: the quantity of product j to produce
array[Products] of var 0..max(u): X;

% the total profit, to be maximized
var int: objective = sum(j in Products)(c[j] * X[j]);

% the product of the a[j] is a common multiple of all the a[j], so multiplying by it clears the fractions
int: scale = product(j in Products)(a[j]);

% the sum of X[j] / a[j] over all products is at most b (written without fractions)
constraint sum(j in Products)((scale div a[j]) * X[j]) <= b * scale;

% each quantity X[j] is at most its upper bound u[j]
constraint forall(j in Products)(X[j] <= u[j]);

solve maximize objective;

output ["{\"x\": ", showJSON(X), ", \"total_profit\": ", showJSON(objective), "}"];
