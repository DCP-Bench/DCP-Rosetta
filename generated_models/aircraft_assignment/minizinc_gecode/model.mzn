% aircraft_assignment: a MiniZinc model from DCP Rosetta.
%
% Assign multiple types of aircraft to a set of routes to minimize the total operational cost. Each
% aircraft type has a limited number of available units. Each route has a specific passenger demand that
% must be satisfied. For each aircraft type and route, we are given the passenger capacity and the
% operational cost. Determine how many aircraft of each type to assign to each route so that all passenger
% demands are met, the availability limit of each aircraft type is respected, and the overall cost is minimal.
%
% Save this file as model.mzn. Download `aircraft_assignment.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_assignment.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py aircraft_assignment.json
%   minizinc model.mzn aircraft_assignment_1.json

array[int] of int: availability;               % availability[i]: aircraft of type i available
array[int] of int: demand;                     % demand[j]: passengers to carry on route j
array[int, int] of int: capabilities;          % capabilities[i,j]: passengers one aircraft of type i carries on route j
array[int, int] of int: costs;                 % costs[i,j]: operational cost of one aircraft of type i on route j

set of int: Types = index_set(availability);
set of int: Routes = index_set(demand);

% allocation[i,j]: number of aircraft of type i assigned to route j, at most the fleet of type i
array[Types, Routes] of var 0..max(availability): allocation;

% the aircraft of each type assigned to all routes do not exceed its availability
constraint forall(i in Types)(sum(j in Routes)(allocation[i, j]) <= availability[i]);

% the passengers carried on each route meet its demand
constraint forall(j in Routes)(sum(i in Types)(capabilities[i, j] * allocation[i, j]) >= demand[j]);

% the total operational cost of the assignment
var int: objective = sum(i in Types, j in Routes)(costs[i, j] * allocation[i, j]);

solve minimize objective;

output ["{\"allocation\": ", showJSON(allocation), "}"];
