% curious_set_of_integers: a SWI-Prolog model from DCP Rosetta.
%
% The integers 1, 3, 8 and 120 form a set with a remarkable property: the product of any two integers is one less
% than a perfect square. Find a fifth number (larger than or equal to 0) that can be added to the set without
% destroying this property.
%
% Save this file as model.pl. Download `curious_set_of_integers.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/curious_set_of_integers.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('curious_set_of_integers.json')" -t halt model.pl
%
% Data fields: max_val (the largest value the fifth number can take).
:- use_module(library(clpfd)).

model(Instance, [Number, Roots], [number-Number]) :-
    MaxVal = Instance.max_val,
    Set = [1, 3, 8, 120],
    % the fifth number is between 0 and the bound, and it is different from the four numbers of the set
    Number in 0..MaxVal,
    maplist({Number}/[A]>>(Number #\= A), Set),
    % the product of the fifth number and each number of the set, plus one, is a perfect square: R * R
    max_list(Set, Largest), MaxRoot is Largest * MaxVal + 1,
    maplist({Number, MaxRoot}/[A, R]>>(R in 0..MaxRoot, R * R #= A * Number + 1), Set, Roots).

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
