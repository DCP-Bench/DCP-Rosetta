% room_assignment: an ECLiPSe model from DCP Rosetta.
%
% The room assignment problem involves assigning a set of requests to a limited number of rooms such that each request
% is assigned to one room for its entire duration. Some requests may already have a room pre-assigned. The main
% constraint is that a room can only serve one request at a time, meaning no overlapping requests can be assigned to
% the same room. A request occupies its room from its start date up to, but not including, its end date, so one request
% can start in a room on the day another ends there. A pre-assigned room of -1 means that the request has none.
%
% Save this file as model.ecl. Download `room_assignment.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/room_assignment.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py room_assignment.json
%   eclipse -b model.ecl -e "run('room_assignment_1.dat'), halt"
%
% The data fields: max_rooms is the number of rooms; start_data and end_data hold the start and the end date of each
% request as YYYY-MM-DD strings; preassigned_room_data holds the room each request already has, -1 when it has none.
% All lists are indexed from 0 as in the JSON.

:- lib(ic).
:- lib(listut).

% Output room_assignments: the room of each request, a number from 0 to max_rooms - 1.
model(Instance, Rooms, [room_assignments-Rooms]) :-
    memberchk(max_rooms-MaxRooms, Instance),
    memberchk(start_data-Starts, Instance),
    memberchk(end_data-Ends, Instance),
    memberchk(preassigned_room_data-Preassigned, Instance),
    length(Starts, NRequests),
    length(Rooms, NRequests),
    Rooms :: 0..MaxRooms-1,

    % a request with a pre-assigned room keeps that room
    ( foreach(Pre, Preassigned), foreach(Room, Rooms) do
        ( Pre >= 0 -> Room #= Pre ; true )
    ),

    % the dates as numbers that order the days the same way
    ( foreach(S, Starts), foreach(K, StartKeys) do date_key(S, K) ),
    ( foreach(E, Ends), foreach(K, EndKeys) do date_key(E, K) ),

    % two requests whose periods overlap (one starts before the other ends) get different rooms
    ( for(I, 1, NRequests), param(NRequests, StartKeys, EndKeys, Rooms) do
        ( for(J, I+1, NRequests), param(I, StartKeys, EndKeys, Rooms) do
            nth1(I, StartKeys, SI), nth1(I, EndKeys, EI),
            nth1(J, StartKeys, SJ), nth1(J, EndKeys, EJ),
            ( SI < EJ, SJ < EI ->
                nth1(I, Rooms, RI), nth1(J, Rooms, RJ), RI #\= RJ
            ;   true
            )
        )
    ).

% The day of a YYYY-MM-DD date as a number: later dates have larger numbers.
date_key(Date, Key) :-
    string_list(Date, [Y1, Y2, Y3, Y4, _, M1, M2, _, D1, D2]),
    Year is 1000*(Y1-0'0) + 100*(Y2-0'0) + 10*(Y3-0'0) + (Y4-0'0),
    Month is 10*(M1-0'0) + (M2-0'0),
    Day is 10*(D1-0'0) + (D2-0'0),
    Key is (Year*12 + Month)*31 + Day.

:- lib(branch_and_bound).

% Reads the data file, builds the model, solves it and prints each output.
run(File) :-
    open(File, read, Stream), read(Stream, Instance), close(Stream),
    solve_model(Instance).

solve_model(Instance) :-
    (   current_module(gfd) -> Lib = gfd ; Lib = ic ),
    (   current_predicate(model/4)
    ->  model(Instance, Vars, Outputs, Objective)
    ;   model(Instance, Vars, Outputs), Objective = none
    ),
    (   Objective = max(Expr)
    ->  call(Lib:(Total #= Expr)), call(Lib:(Cost #= -Total)),
        minimize(run_search(Vars, Outputs), Cost)
    ;   Objective = min(Expr)
    ->  call(Lib:(Cost #= Expr)),
        minimize(run_search(Vars, Outputs), Cost)
    ;   run_search(Vars, Outputs)
    ),
    ( foreach(Name-Value, Outputs) do printf("%w = %w%n", [Name, Value]) ).

run_search(Vars, Outputs) :-
    (   current_predicate(search_goal/1) -> search_goal(Vars) ; labeling(Vars) ),
    term_variables(Outputs, Free),
    labeling(Free).
