% car_selection: a clingo model from DCP Rosetta.
%
% This problem aims to assign participants to cars to maximize the total number of assignments. Each
% participant may be interested in a subset of the available cars. Each participant is assigned to at most one
% car, and each car is assigned to at most one participant.
%
% Save this file as model.lp. Download `car_selection.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/car_selection.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py car_selection.json
%   python -m clingo model.lp car_selection_1.lp

% Input: possible_assignments(I, J, B): B is 1 when participant I is interested in car J and 0 when not
% (indices are 0-based, as in the data).

participant(I) :- possible_assignments(I, _, _).
car(J) :- possible_assignments(_, J, _).

% assign(I, J): participant I gets car J; only cars the participant is interested in can be assigned
{ assign(I, J) } :- possible_assignments(I, J, 1).

% each participant is assigned to at most one car
:- participant(I), #count { J : assign(I, J) } > 1.

% each car is assigned to at most one participant
:- car(J), #count { I : assign(I, J) } > 1.

% the number of assignments is as large as possible
#maximize { 1, I, J : assign(I, J) }.

% assignments(I, J, true) if participant I is assigned to car J, and false otherwise
assignments(I, J, true) :- assign(I, J).
assignments(I, J, false) :- participant(I), car(J), not assign(I, J).

#show assignments/3.
