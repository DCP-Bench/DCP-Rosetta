% room_assignment: a SWI-Prolog model from DCP Rosetta.
%
% Assign a set of requests to a limited number of rooms so that each request is given one room for its entire
% duration. Some requests may already have a room pre-assigned. A room can serve only one request at a time, so no
% two overlapping requests may share a room. A request occupies its room from its start date up to, but not
% including, its end date, so one request can start in a room on the day another ends there. A pre-assigned room of
% -1 means that the request has none.
%
% Save this file as model.pl. Download `room_assignment.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/room_assignment.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('room_assignment.json')" -t halt model.pl
%
% Data fields: max_rooms (the number of rooms, numbered from 0), start_data (the first day of each request,
% YYYY-MM-DD), end_data (the day each request ends, YYYY-MM-DD, not occupied), preassigned_room_data (the room
% already given to each request, or -1); lists indexed from 0.
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(date)).

model(Instance, Rooms, [room_assignments-Rooms]) :-
    MaxRooms = Instance.max_rooms,
    Last is MaxRooms - 1,
    Preassigned = Instance.preassigned_room_data,
    length(Preassigned, NumRequests),      % the number of requests
    length(Rooms, NumRequests),            % Rooms[I] is the room given to request I
    Rooms ins 0..Last,
    maplist(date_stamp, Instance.start_data, Starts),
    maplist(date_stamp, Instance.end_data, Ends),
    % a request that already has a room keeps it
    maplist(keep_preassigned, Rooms, Preassigned),
    % a room serves one request at a time: requests that run on the same day are in different rooms; two
    % overlapping requests both run on the later of their start days, so checking each start day is enough
    maplist(rooms_distinct_on(Rooms, Starts, Ends), Starts).

% date_stamp(+Date, -Stamp): the time stamp of a date written as YYYY-MM-DD.
date_stamp(Date, Stamp) :-
    parse_time(Date, iso_8601, Stamp).

% keep_preassigned(?Room, +Pre): Pre is the room already given, or -1 for none.
keep_preassigned(Room, Pre) :-
    (   Pre =:= -1
    ->  true
    ;   Room #= Pre
    ).

% rooms_distinct_on(+Rooms, +Starts, +Ends, +Day): the requests running on Day are all in different rooms.
rooms_distinct_on(Rooms, Starts, Ends, Day) :-
    running_on(Day, Starts, Ends, Rooms, Running),
    all_distinct(Running).

% running_on(+Day, +Starts, +Ends, +Rooms, -Running): Running lists the rooms of the requests that run on Day,
% that is, start on or before Day and end after it.
running_on(_, [], [], [], []).
running_on(Day, [Start|Starts], [End|Ends], [Room|Rooms], Running) :-
    (   Start =< Day, Day < End
    ->  Running = [Room|Rest]
    ;   Running = Rest
    ),
    running_on(Day, Starts, Ends, Rooms, Rest).

:- use_module(library(http/json)).

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
solve_file(File) :- solve_file(File, 1).
solve_file(File, N) :-
    setup_call_cleanup(open(File, read, Stream),
                       json_read_dict(Stream, Data, [value_string_as(atom)]),
                       close(Stream)),
    (   is_list(Data) -> nth1(N, Data, Instance) ; Instance = Data ),
    solve_model(Instance).

solve_model(Instance) :-
    (   current_predicate(model/4)
    ->  model(Instance, Vars, Outputs, Objective)
    ;   model(Instance, Vars, Outputs), Objective = none
    ),
    (   current_predicate(labeling_options/1) -> labeling_options(Options) ; Options = [ff] ),
    term_variables(Vars-Outputs, All),
    (   Objective == none
    ->  labeling(Options, All)
    ;   once(labeling([Objective|Options], All))
    ),
    forall(member(Name-Value, Outputs), format("~w = ~w~n", [Name, Value])).
