% assignment_costs: a SWI-Prolog model from DCP Rosetta.
%
% Assign people to 4 tasks with different costs, so that the total cost is minimized. Each task must be assigned to
% exactly one person, but it is not necessary to assign all people to a task.
%
% Save this file as model.pl. Download `assignment_costs.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/assignment_costs.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('assignment_costs.json')" -t halt model.pl
%
% Data fields: cost (the cost of each task for each person, a list per task indexed from 0, each listing the people
% indexed from 0).
:- use_module(library(clpfd)).

% Rows[I][J] is 1 when task I is assigned to person J, 0 otherwise
model(Instance, Vars, [x-Rows], min(Total)) :-
    Costs = Instance.cost,
    Costs = [FirstRow|_],
    length(FirstRow, NPeople),
    length(Costs, NTasks),
    length(Rows, NTasks),
    maplist(row_of_length(NPeople), Rows),
    append(Rows, Flat),
    Flat ins 0..1,
    Vars = [Total|Flat],
    % each task is assigned to exactly one person
    maplist(exactly_one, Rows),
    % each person is assigned at most one task
    transpose(Rows, Columns),
    maplist(at_most_one, Columns),
    % the total cost of the assignment, to be minimised
    append(Costs, CostList),
    scalar_product(CostList, Flat, #=, Total).

% a row with one entry for each person
row_of_length(N, Row) :-
    length(Row, N).

% exactly one of the entries is 1
exactly_one(Entries) :-
    sum(Entries, #=, 1).

% at most one of the entries is 1
at_most_one(Entries) :-
    sum(Entries, #=<, 1).

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
