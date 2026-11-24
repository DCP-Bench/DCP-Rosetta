% appointment_scheduling: a SWI-Prolog model from DCP Rosetta.
%
% Schedule 4 people into 4 interview slots based on their free-busy schedules, where m[i][j] is 1 if person i is free
% in slot j. Each person gets exactly one slot in which they are free, and each slot goes to exactly one person.
%
% Save this file as model.pl. Download `appointment_scheduling.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/appointment_scheduling.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('appointment_scheduling.json')" -t halt model.pl
%
% Data fields: m (the free-busy schedules: m[i][j] is 1 when person i is free in slot j, a list per person indexed
% from 0).
:- use_module(library(clpfd)).

% Rows[I][J] is 1 when person I is assigned to slot J, 0 otherwise
model(Instance, Vars, [x-Rows]) :-
    Free = Instance.m,
    length(Free, N),
    length(Rows, N),
    maplist(row_of_length(N), Rows),
    append(Rows, Vars),
    Vars ins 0..1,
    % a person is only assigned to a slot in which they are free
    maplist(only_when_free, Rows, Free),
    % each person gets exactly one slot
    maplist(exactly_one, Rows),
    % each slot goes to exactly one person
    transpose(Rows, Columns),
    maplist(exactly_one, Columns).

% a row with one entry for each slot
row_of_length(N, Row) :-
    length(Row, N).

% an assignment is allowed only where the person is free
only_when_free(Row, FreeRow) :-
    maplist(#=<, Row, FreeRow).

% exactly one of the entries is 1
exactly_one(Entries) :-
    sum(Entries, #=, 1).

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
:- use_module(library(http/json)).
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
