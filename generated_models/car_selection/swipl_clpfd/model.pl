% car_selection: a SWI-Prolog model from DCP Rosetta.
%
% Assign participants to cars so as to maximise the total number of assignments. Each participant may be interested
% in only some of the cars, and is assigned only to a car they are interested in. Each participant is assigned to at
% most one car, and each car is assigned to at most one participant.
%
% Save this file as model.pl. Download `car_selection.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/car_selection.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('car_selection.json')" -t halt model.pl
%
% Data fields: possible_assignments (a matrix indexed from 0: row I is participant I, column J is car J, and the
% entry is 1 when participant I is interested in car J).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(yall)).

model(Instance, Vars, [assignments-Rows], max(Total)) :-
    Interest = Instance.possible_assignments,
    length(Interest, P),                   % the number of participants
    Interest = [First|_],
    length(First, C),                      % the number of cars
    length(Rows, P),
    maplist({C}/[Row]>>length(Row, C), Rows),
    append(Rows, Cells),
    Cells ins 0..1,                        % Rows[I][J] = 1 when participant I is assigned to car J
    % a participant is assigned only to a car they are interested in
    append(Interest, FlatInterest),
    maplist(#=<, Cells, FlatInterest),
    % each participant is assigned to at most one car
    maplist([Row]>>sum(Row, #=<, 1), Rows),
    % each car is assigned to at most one participant
    transpose(Rows, Columns),
    maplist([Column]>>sum(Column, #=<, 1), Columns),
    % the total number of assignments, to be maximised
    sum(Cells, #=, Total),
    Vars = [Total|Cells].

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
