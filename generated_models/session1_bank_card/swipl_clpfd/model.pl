% session1_bank_card: a SWI-Prolog model from DCP Rosetta.
%
% My bank card has a 4 digit PIN, abcd. I use the following facts to help me remember it: no two digits are the same;
% the 2-digit number cd is 3 times the 2-digit number ab; and the 2-digit number da is 2 times the 2-digit number bc.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_bank_card.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
:- use_module(library(clpfd)).

% Vars holds the four digits of the PIN, a, b, c and d.
model(_Instance, Vars, [a-A, b-B, c-C, d-D]) :-
    Vars = [A, B, C, D],
    % each digit is from 0 to 9
    Vars ins 0..9,
    % no two digits are the same
    all_distinct(Vars),
    % the 2-digit number cd is 3 times the 2-digit number ab
    10 * C + D #= 3 * (10 * A + B),
    % the 2-digit number da is 2 times the 2-digit number bc
    10 * D + A #= 2 * (10 * B + C).

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
