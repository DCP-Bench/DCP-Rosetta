% aircraft_assignment: a clingo model from DCP Rosetta.
%
% This problem involves assigning multiple types of aircraft to a set of routes to minimize the total operational cost. Each aircraft type has a limited number of available units. Each route has a specific passenger demand that must be satisfied. For each aircraft type and route, we are given the passenger capacity and the operational cost. The goal is to determine how many aircraft of each type to assign to each route to meet all passenger demands, stay within the availability limits for each aircraft type, and minimize the overall cost.
%
% Save this file as model.lp. Download `aircraft_assignment.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_assignment.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py aircraft_assignment.json
%   python -m clingo model.lp aircraft_assignment_1.lp

% Input: availability(I, N): N aircraft of type I are available; demand(J, D): route J needs D
% passengers; capabilities(I, J, C): an aircraft of type I carries C passengers on route J;
% costs(I, J, C): an aircraft of type I costs C to fly route J (indices are 0-based, as in the data).

type(I) :- availability(I, _).
route(J) :- demand(J, _).
most(M) :- M = #max { N : availability(_, N) }.

% allocation(I, J, N): N aircraft of type I fly route J. Each type and route pair gets exactly one count.
1 { allocation(I, J, N) : N = 0..M } 1 :- type(I), route(J), most(M).

% the aircraft of each type assigned to the routes do not exceed the number available
:- availability(I, A), A < #sum { N, J : allocation(I, J, N) }.

% the aircraft on each route together carry at least the passengers demanded on that route
:- demand(J, D), D > #sum { C * N, I : allocation(I, J, N), capabilities(I, J, C) }.

% minimize the total operational cost of all the aircraft flown
#minimize { C * N, I, J : allocation(I, J, N), costs(I, J, C) }.

#show allocation/3.
