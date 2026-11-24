% appointment_scheduling: a clingo model from DCP Rosetta.
%
% Schedule 4 people into 4 interview slots based on their free-busy schedules, where m[i][j] is 1 if person i is free in slot j. Each person gets exactly one slot in which they are free, and each slot goes to exactly one person.
%
% Save this file as model.lp. Download `appointment_scheduling.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/appointment_scheduling.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py appointment_scheduling.json
%   python -m clingo model.lp appointment_scheduling_1.lp

% Input: m(I, J, V): V is 1 when person I is free in slot J and 0 when busy (indices are 0-based, as in the data).

person(I) :- m(I, _, _).
slot(J) :- m(_, J, _).

% assigned(I, J): person I is given slot J. Each person gets exactly one slot.
1 { assigned(I, J) : slot(J) } 1 :- person(I).

% each slot goes to exactly one person
1 { assigned(I, J) : person(I) } 1 :- slot(J).

% a person is given only a slot in which they are free
:- assigned(I, J), m(I, J, 0).

% x(I, J, true) when person I is assigned to slot J, and x(I, J, false) otherwise
x(I, J, true) :- assigned(I, J).
x(I, J, false) :- person(I), slot(J), not assigned(I, J).

#show x/3.
