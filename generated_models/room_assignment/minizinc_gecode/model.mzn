% room_assignment: a MiniZinc model from DCP Rosetta.
%
% The room assignment problem involves assigning a set of requests to a limited number of rooms such that each
% request is assigned to one room for its entire duration. Some requests may already have a room pre-assigned. The main
% constraint is that a room can only serve one request at a time, meaning no overlapping requests can be assigned to
% the same room. A request occupies its room from its start date up to, but not including, its end date, so one request
% can start in a room on the day another ends there. A pre-assigned room of -1 means that the request has none.
%
% Save this file as model.mzn. Download `room_assignment.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/room_assignment.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py room_assignment.json
%   minizinc model.mzn room_assignment_1.json

int: max_rooms;                                    % the rooms are 0 .. max_rooms-1
array[int] of string: start_data;                  % start date of each request, "YYYY-MM-DD"
array[int] of string: end_data;                    % end date of each request, "YYYY-MM-DD"
array[int] of int: preassigned_room_data;          % the room a request already has, -1 if none

set of int: Requests = index_set(start_data);      % one index per request

% the day number of a date: its Julian day number, so that differences are numbers of days
array[int] of string: digit_chars = string_split("0123456789", "");
function int: digit(string: c) = min([i - 1 | i in index_set(digit_chars) where digit_chars[i] = c]);
function int: number_at(array[int] of string: chars, int: from, int: to) =
    sum(i in from..to)(digit(chars[i]) * pow(10, to - i));
function int: day_number(string: date) =
    let { array[int] of string: ch = string_split(date, "");
          int: y = number_at(ch, 1, 4);
          int: m = number_at(ch, 6, 7);
          int: d = number_at(ch, 9, 10);
          int: a = (14 - m) div 12;
          int: yy = y + 4800 - a;
          int: mm = m + 12 * a - 3 }
    in d + (153 * mm + 2) div 5 + 365 * yy + yy div 4 - yy div 100 + yy div 400 - 32045;

array[Requests] of int: first_day = [day_number(start_data[r]) | r in Requests];
array[Requests] of int: last_day_excl = [day_number(end_data[r]) | r in Requests];   % the end day is not occupied

array[Requests] of var 0..max_rooms - 1: room_assignments;   % room_assignments[r]: the room request r is in

% a request with a pre-assigned room is in that room
constraint forall(r in Requests where preassigned_room_data[r] != -1)
    (room_assignments[r] = preassigned_room_data[r]);

% a room serves only one request at a time: two requests that overlap in time are in different rooms
constraint forall(r1, r2 in Requests where r1 < r2 /\
                  first_day[r1] < last_day_excl[r2] /\ first_day[r2] < last_day_excl[r1])
    (room_assignments[r1] != room_assignments[r2]);

solve satisfy;
output ["{\"room_assignments\": ", showJSON(room_assignments), "}"];
