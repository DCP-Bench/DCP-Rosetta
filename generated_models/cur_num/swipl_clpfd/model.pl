% cur_num: a SWI-Prolog model from DCP Rosetta.
%
% The number 48 has this peculiarity: if you add 1 to it the result is a square number, and if you add 1 to its half,
% you also get a square number. Find another number with this peculiarity, between 1 and 10000.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/cur_num.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
:- use_module(library(clpfd)).

model(_Instance, [Peculiar, A, B, C, D, E], [peculiar-Peculiar]) :-
    % the number is between 1 and 10000, and it is another number than 48
    [Peculiar, A, B, C, D, E] ins 1..10000,
    Peculiar #\= 48,
    % adding 1 to the number gives a square: A = B * B, with B non-negative
    Peculiar + 1 #= A,
    A #= B * B,
    B #>= 0,
    % the number is even, its half C, and adding 1 to the half gives a square: D = E * E
    Peculiar #= 2 * C,
    C + 1 #= D,
    D #= E * E,
    E #>= 0.

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
