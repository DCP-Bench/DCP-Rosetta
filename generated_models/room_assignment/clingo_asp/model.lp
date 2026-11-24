% room_assignment: a clingo model from DCP Rosetta.
%
% The room assignment problem involves assigning a set of requests to a limited number of rooms such that each request is assigned to one room for its entire duration. Some requests may already have a room pre-assigned. The main constraint is that a room can only serve one request at a time, meaning no overlapping requests can be assigned to the same room. A request occupies its room from its start date up to, but not including, its end date, so one request can start in a room on the day another ends there. A pre-assigned room of -1 means that the request has none.
%
% Save this file as model.lp. Download `room_assignment.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/room_assignment.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py room_assignment.json
%   python -m clingo model.lp room_assignment_1.lp

% Input: max_rooms(M): the number of rooms M; start_data(I, D) and end_data(I, D): the start and end
% date D of request I as "YYYY-MM-DD" strings, which compare in date order; preassigned_room_data(I, R):
% the room R already assigned to request I, or -1 for none (indices are 0-based, as in the data).

request(I) :- start_data(I, _).

% each request is assigned to exactly one room, from 0 to max_rooms - 1
1 { room_assignments(I, R) : R = 0..M-1 } 1 :- request(I), max_rooms(M).

% a request with a pre-assigned room keeps that room
:- preassigned_room_data(I, R), R != -1, not room_assignments(I, R).

% two requests overlap when they both occupy some day d with start <= d < end
overlap(I, J) :- request(I), request(J), I < J,
                 start_data(I, SI), end_data(I, EI), start_data(J, SJ), end_data(J, EJ),
                 SI < EI, SJ < EJ, SI < EJ, SJ < EI.

% overlapping requests are not assigned the same room
:- overlap(I, J), room_assignments(I, R), room_assignments(J, R).

#show room_assignments/2.
