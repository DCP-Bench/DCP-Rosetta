% coin3_application: a SWI-Prolog model from DCP Rosetta.
%
% Find the minimum number of coins, of the given denominations, that allow one to pay exactly any amount smaller than
% a given maximum amount.
%
% Save this file as model.pl. Download `coin3_application.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/coin3_application.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('coin3_application.json')" -t halt model.pl
%
% Data fields: denominations (the value of each kind of coin, lists indexed from 0), max_amount_to_pay (every
% amount from 1 up to one less than this must be payable).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).

model(Instance, Vars, [x-X], min(NumCoins)) :-
    Denominations = Instance.denominations,
    MaxAmount = Instance.max_amount_to_pay,
    length(Denominations, K),              % the number of kinds of coin
    Last is MaxAmount - 1,                 % the largest amount that must be payable
    % X[I] = number of coins of kind I in the purse; a purse never needs more than Last coins of one kind
    length(X, K),
    X ins 0..Last,
    % the number of coins in the purse, to be minimised
    sum(X, #=, NumCoins),
    % every amount from 1 to Last can be paid with the coins of the purse
    numlist(1, Last, Amounts),
    maplist(payable(Denominations, X), Amounts, Uses),
    append(Uses, UseVars),
    append([[NumCoins], X, UseVars], Vars).

% Amount can be paid from the purse X: Used[I] coins of kind I, no more than the purse holds, add up to Amount
payable(Denominations, X, Amount, Used) :-
    length(X, K),
    length(Used, K),
    Used ins 0..Amount,
    maplist(#=<, Used, X),
    scalar_product(Denominations, Used, #=, Amount).

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
