% birthday_coins: a SWI-Prolog model from DCP Rosetta.
%
% Tommy was given 15 coins for his birthday. Each coin is a half-crown, a shilling or a sixpence, but he was not
% necessarily given coins of all three kinds. The coins add up to one pound, five shillings and sixpence. A pound is
% 20 shillings and a shilling is 12 pence, so a half-crown is 30 pence, a shilling 12 pence and a sixpence 6 pence.
% Find how many half-crowns he could have been given.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/birthday_coins.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
:- use_module(library(clpfd)).

model(_Instance, Vars, [half_crowns-HalfCrowns]) :-
    % the numbers of half-crowns, shillings and sixpences
    Coins = [HalfCrowns, Shillings, Sixpences],
    Coins ins 0..15,
    sum(Coins, #=, 15),                     % fifteen coins in all
    % one pound, five shillings and sixpence is 240 + 60 + 6 = 306 pence
    % pence values: half-crown 30, shilling 12, sixpence 6
    scalar_product([30, 12, 6], Coins, #=, 306),
    Vars = Coins.

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
