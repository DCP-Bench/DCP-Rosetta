% netasgn: a MiniZinc model from DCP Rosetta.
%
% Consider a project assignment problem. Given a set of people and a set of projects. Each person has a
% certain number of available hours and each project requires a certain number of hours. The cost per hour
% of work for a person on a project is given. Each person can contribute to a project up to a maximum limit
% of hours. The problem aims to minimize the total cost of assigning people to projects. It is constrained
% that the total number of hours assigned from each person equals its supply and the total number of hours
% assigned to each project equals its demand.
%
% Save this file as model.mzn. Download `netasgn.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/netasgn.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py netasgn.json
%   minizinc model.mzn netasgn_1.json

array[int] of int: supply;               % supply[i]: hours available from person i
array[int] of int: demand;               % demand[j]: hours required by project j
array[int,int] of int: cost;             % cost[i,j]: cost per hour of person i on project j
array[int,int] of int: limit;            % limit[i,j]: most hours person i can work on project j

set of int: People = index_set(supply);
set of int: Projects = index_set(demand);

% assign[i,j]: hours person i works on project j
array[People, Projects] of var 0..max(limit): assign;

% the total cost of the hours assigned
var int: objective = sum(i in People, j in Projects)(cost[i,j] * assign[i,j]);

% the hours assigned from each person equal its supply
constraint forall(i in People)(sum(j in Projects)(assign[i,j]) = supply[i]);

% the hours assigned to each project equal its demand
constraint forall(j in Projects)(sum(i in People)(assign[i,j]) = demand[j]);

% each person works on a project up to its limit
constraint forall(i in People, j in Projects)(assign[i,j] <= limit[i,j]);

solve minimize objective;

output ["{\"assign\": ", showJSON(assign), ", \"total_cost\": ", showJSON(objective), "}"];
