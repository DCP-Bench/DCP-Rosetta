% mario: a MiniZinc model from DCP Rosetta.
%
% Mario needs to collect as much gold as possible by visiting different houses. He starts at Mario's
% house and ends at Luigi's house. Each house has a certain amount of gold and the travel between houses
% consumes fuel. Mario has a limited amount of fuel, and he needs to plan his route to maximize the gold
% collected without exceeding the fuel limit.
%
% Save this file as model.mzn. Download `mario.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/mario.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py mario.json
%   minizinc model.mzn mario_1.json

include "globals.mzn";

int: nHouses;                              % the number of houses
int: marioHouse;                           % Mario's house (houses are numbered from 0)
int: luigiHouse;                           % Luigi's house (houses are numbered from 0)
int: fuelLimit;                            % the fuel Mario has
array[int, int] of int: arc_fuel;          % arc_fuel[i,j]: fuel used to travel from house i to house j
array[int] of int: goldInHouse;            % goldInHouse[i]: gold in house i

% MiniZinc arrays start at 1, so house i of the data is index i+1 in the model
set of int: Houses = 1..nHouses;
int: mario = marioHouse + 1;
int: luigi = luigiHouse + 1;

% s[i]: the house visited after house i; s[i] = i if house i is not on the route
array[Houses] of var Houses: s;

% the houses on the route form a single cycle, and the houses not on the route are fixed points
constraint subcircuit(s);

% Mario starts at his house, so his house is on the route
constraint s[mario] != mario;

% Mario ends at Luigi's house and returns to Mario's house
constraint s[luigi] = mario;

% the fuel used by the arcs of the route does not exceed the fuel limit (the arc from Luigi's house back to Mario's only closes the cycle and uses no fuel)
constraint sum(i in Houses where i != luigi)(if s[i] != i then arc_fuel[i, s[i]] else 0 endif) <= fuelLimit;

% gold collected: the gold in every house visited on the route
var int: objective = sum(i in Houses)(if s[i] != i then goldInHouse[i] else 0 endif);

solve maximize objective;

output ["{\"s\": ", showJSON([s[i] - 1 | i in Houses]), "}"];
