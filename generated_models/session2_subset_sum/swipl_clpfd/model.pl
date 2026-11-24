% session2_subset_sum: a SWI-Prolog model from DCP Rosetta.
%
% A bank van had several bags of coins, each bag holding a number of coins from a given list, and there are several
% bags of each kind. While the van was parked on the street, thieves stole some of the bags, and a given total number
% of coins was lost. Find how many bags were stolen for each kind of coin bag.
%
% Save this file as model.pl. Download `session2_subset_sum.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subset_sum.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('session2_subset_sum.json')" -t halt model.pl
%
% Data fields: coin_numbers (the number of coins in each kind of bag, lists indexed from 0) and total_coins_lost
% (the number of coins lost).
:- use_module(library(clpfd)).

model(Instance, Bags, [bags-Bags]) :-
    Coins = Instance.coin_numbers,
    Lost = Instance.total_coins_lost,
    length(Coins, N),                      % the number of kinds of bag
    length(Bags, N),
    Bags ins 0..Lost,                      % the number of bags stolen of each kind
    % the stolen bags hold exactly the coins lost
    scalar_product(Coins, Bags, #=, Lost).

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
