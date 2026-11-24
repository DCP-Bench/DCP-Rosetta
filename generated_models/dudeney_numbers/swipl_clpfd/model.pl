% dudeney_numbers: a SWI-Prolog model from DCP Rosetta.
%
% A Dudeney Number is a positive integer that is a perfect cube such that the sum of its digits is equal to the cube
% root of the number. Find such a number that is also larger than 1 and has at most n digits.
%
% Save this file as model.pl. Download `dudeney_numbers.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/dudeney_numbers.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('dudeney_numbers.json')" -t halt model.pl
%
% Data fields: n (the largest number of digits the Dudeney number may have).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(yall)).

model(Instance, [Root, Number, Digits], [number-Number]) :-
    N = Instance.n,                    % the most digits the number may have
    Largest is 10^N - 1,               % the largest number with at most N digits
    MaxRoot is integer(Largest ** (1.0/3)) + 1,
    Root in 1..MaxRoot,                % the cube root of the number
    Number in 2..Largest,              % larger than 1
    Number #= Root^3,                  % a perfect cube
    % the digits of the number, most significant first
    length(Digits, N),
    Digits ins 0..9,
    numlist(1, N, Places),
    maplist({N}/[P, W]>>(W is 10^(N - P)), Places, Weights),
    scalar_product(Weights, Digits, #=, Number),
    % the sum of the digits is equal to the cube root
    sum(Digits, #=, Root).

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
