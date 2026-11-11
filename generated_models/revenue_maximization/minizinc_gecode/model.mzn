% revenue_maximization: a MiniZinc model from DCP Rosetta.
%
% We have a set of flight legs (one-way non-stop flight) with a limited passenger capacity. According to market research,
% we defined a set of flight itineraries to sell as a package with a given price. For each package, we have an estimated
% demand. How many units of each package should we sell to maximize the revenue? We reserve the passenger seats according
% to the number of packages we want to sell.
%
% Save this file as model.mzn. Download `revenue_maximization.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/revenue_maximization.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py revenue_maximization.json
%   minizinc model.mzn revenue_maximization_1.json

array[int] of int: available_seats;          % the passenger seats of each flight leg
array[int] of int: demand;                   % the estimated demand for each package
array[int] of int: revenue;                  % the price of one unit of each package
array[int, int] of int: delta;               % delta[i,j]: seats of flight leg j that one unit of package i reserves

set of int: Packages = index_set(demand);    % one index per package
set of int: Legs = index_set(available_seats); % one index per flight leg

array[Packages] of var int: packages_to_sell; % packages_to_sell[i]: units of package i sold

% the seats reserved on each flight leg do not exceed its passenger capacity
constraint forall(j in Legs)
    (sum(i in Packages)(delta[i, j] * packages_to_sell[i]) <= available_seats[j]);

% no more units of a package are sold than its estimated demand
constraint forall(i in Packages)(packages_to_sell[i] >= 0 /\ packages_to_sell[i] <= demand[i]);

var int: objective = sum(i in Packages)(revenue[i] * packages_to_sell[i]);

solve maximize objective;
output ["{\"packages_to_sell\": ", showJSON(packages_to_sell), ", \"max_revenue\": ", show(objective), "}"];
