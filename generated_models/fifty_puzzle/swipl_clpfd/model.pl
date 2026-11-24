% fifty_puzzle: a SWI-Prolog model from DCP Rosetta.
%
% A side show is described as follows: "There were a number of little dummies which you were to knock over with
% baseballs. The man said: 'Take as many throws as you like at a cent apiece and stand as close as you please. Add up
% the numbers on all the men that you knock down and when the sum amounts to exactly a given target sum, neither more
% nor less you get a genuine prize.'" The numbers on the dummies are given as a list of integers.
%
% Save this file as model.pl. Download `fifty_puzzle.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/fifty_puzzle.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('fifty_puzzle.json')" -t halt model.pl
%
% Data fields: values (the number written on each dummy, lists indexed from 0), target_sum (the sum that the knocked
% over dummies must amount to exactly).
:- use_module(library(clpfd)).
:- use_module(library(lists)).

model(Instance, Dummies, [dummies-Dummies]) :-
    Values = Instance.values,          % the number on each dummy
    Target = Instance.target_sum,      % the sum the knocked over dummies must amount to
    length(Values, N),                 % the number of dummies
    length(Dummies, N),
    % Dummies[D] is 1 when dummy D is knocked over, and a knocked over dummy counts once
    Dummies ins 0..1,
    % the numbers on the knocked over dummies sum to exactly the target
    scalar_product(Values, Dummies, #=, Target).

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
