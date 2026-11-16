% five_statements: a SWI-Prolog model from DCP Rosetta.
%
% Determine which of the following five statements is true. Statement 1: exactly one of these statements is false.
% Statement 2: exactly two of these statements are false. Statement 3: exactly three of these statements are false.
% Statement 4: exactly four of these statements are false. Statement 5: exactly five of these statements are false.
% Each statement is either true or false.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/five_statements.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
%
% No data fields: the model reads nothing from the data.
:- use_module(library(clpfd)).

model(_Instance, Ss, [statements-Ss]) :-
    length(Ss, 5),
    Ss ins 0..1,                          % 1 when the statement is true
    numlist(1, 5, Ks),
    % statement K is true exactly when K of the five statements are false
    maplist(statement_holds(Ss), Ks, Ss).

statement_holds(Ss, K, S) :-
    falses(Ss, Fs),
    sum(Fs, #=, Count),
    S #<==> (Count #= K).

falses([], []).
falses([S|Ss], [F|Fs]) :-
    F #= 1 - S,
    falses(Ss, Fs).

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
