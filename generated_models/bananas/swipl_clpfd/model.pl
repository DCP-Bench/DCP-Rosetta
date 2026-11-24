% bananas: a SWI-Prolog model from DCP Rosetta.
%
% Five bananas cost three dollars, seven oranges cost five dollars, nine mangoes cost seven dollars, and three apples
% cost nine dollars. Buy 100 fruits for exactly 100 dollars, buying every kind of fruit at least once, so that the
% number of bananas and apples together is as small as possible.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/bananas.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
:- use_module(library(clpfd)).

model(_Instance, Vars, [bananas-Bananas, oranges-Oranges, mangoes-Mangoes, apples-Apples], min(Total)) :-
    Fruits = [Bananas, Oranges, Mangoes, Apples],
    Fruits ins 1..100,                      % every kind of fruit is bought, at least one
    sum(Fruits, #=, 100),                   % 100 fruits in all
    % a banana costs 3/5 dollar, an orange 5/7, a mango 7/9 and an apple 3 dollars; multiplied by 315 (the least
    % common multiple of 5, 7 and 9) the total cost must be 100 * 315 = 31500
    189 * Bananas + 225 * Oranges + 245 * Mangoes + 945 * Apples #= 31500,
    Total #= Bananas + Apples,              % the bananas and apples together, to be made as small as possible
    Vars = [Total|Fruits].

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
