% session3_kidney_exchange: a SWI-Prolog model from DCP Rosetta.
%
% At a hospital n people are on a waiting list for a kidney transplant. The compatibility between them is a directed
% graph: compatible[i] is the set of people to which person i can donate. Maximise the number of people who receive a
% new kidney: anyone who gives a kidney must receive one, and no person receives more than one kidney.
%
% Save this file as model.pl. Download `session3_kidney_exchange.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_kidney_exchange.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('session3_kidney_exchange.json')" -t halt model.pl
%
% Data fields: num_people (the number of people on the list) and compatible (for each person in list order, the
% people to which that person can donate, numbered from 1 as in the data).
:- use_module(library(clpfd)).

model(Instance, Cells, [transplants-Rows], max(Total)) :-
    N = Instance.num_people,
    Compatible = Instance.compatible,
    % Rows[I][J] = 1 when person I donates to person J; only compatible pairs may be chosen
    maplist(donor_row(N), Compatible, Rows),
    append(Rows, Cells),
    Cells ins 0..1,
    % each person gives at most one kidney, and each person receives at most one
    maplist(at_most_one, Rows),
    transpose(Rows, Columns),
    maplist(at_most_one, Columns),
    % anyone who gives a kidney must receive one
    maplist(giver_receives, Rows, Columns),
    % the number of people who receive a kidney
    sum(Cells, #=, Total).

donor_row(N, Compatible, Row) :-
    length(Row, N),
    numlist(1, N, Ids),
    maplist(may_donate_to(Compatible), Ids, Row).

may_donate_to(Compatible, Id, X) :-
    (   memberchk(Id, Compatible) -> true ; X #= 0 ).

at_most_one(Line) :- sum(Line, #=<, 1).

giver_receives(Gives, Receives) :-
    sum(Gives, #=, G),
    sum(Receives, #=, R),
    G #=< R.

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
