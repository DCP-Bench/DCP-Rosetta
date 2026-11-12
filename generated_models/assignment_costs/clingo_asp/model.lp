% assignment_costs: a clingo model from DCP Rosetta.
%
% Assign people to tasks with different costs, so that the total cost is minimized. Each task must be assigned to exactly one person, but it is not necessary to assign all people to a task.
%
% Save this file as model.lp. Download `assignment_costs.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/assignment_costs.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py assignment_costs.json
%   python -m clingo model.lp assignment_costs_1.lp

% Input: cost(I, J, C) holds the cost C of assigning task I to person J (indices are 0-based).

task(I) :- cost(I, _, _).
person(J) :- cost(_, J, _).

% each task is assigned to exactly one person
1 { assigned(I, J) : person(J) } 1 :- task(I).

% each person is given at most one task
:- person(J), #count { I : assigned(I, J) } > 1.

% the output x(I, J, V) is true for the assigned pairs and false for the others
x(I, J, true) :- assigned(I, J).
x(I, J, false) :- task(I), person(J), not assigned(I, J).

% the total cost of the assignment is as small as possible
#minimize { C, I, J : assigned(I, J), cost(I, J, C) }.

#show x/3.
