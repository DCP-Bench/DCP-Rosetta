% football: a SWI-Prolog model from DCP Rosetta.
%
% A Premiership team wants to spend as much money as it can on players, up to a limit of GBP 30 million, buying a
% total as close to that figure as possible without going over. Available players, with prices in GBP millions:
% goalkeepers g1 0.73, g2 1.28, g3 3.88 (buy exactly 1); defenders d1 0.92, d2 1.31, d3 1.62, d4 2.41, d5 2.79,
% d6 3.28, d7 3.91, d8 4.57 (buy 2 or more); midfielders m1 1.8, m2 2.63, m3 3.17, m4 3.769, m5 4.14, m6 4.75,
% m7 5.38, m8 5.93, m9 6.78, m10 7.13 (buy 3 or more); strikers s1 4.46, s2 6.47, s3 7.78, s4 8.39, s5 9.5 (buy 2 or
% more). The team must buy at least eleven players in total. Give the total price in GBP thousands (z), so that
% GBP 12.345 million is 12345.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/football.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
%
% No data fields: the prices are fixed in the model, in GBP thousands.
:- use_module(library(clpfd)).

% search heuristic: the strikers (the dearest group) are labelled first, in list order, each tried as bought (1) before not bought (0)
labeling_options([down]).

model(_Instance, Vars, [z-Cost], max(Cost)) :-
    Goalkeepers = [730, 1280, 3880],
    Defenders = [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570],
    Midfielders = [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130],
    Strikers = [4460, 6470, 7780, 8390, 9500],
    choices(Goalkeepers, Gk),           % 1 when the player is bought
    choices(Defenders, Df),
    choices(Midfielders, Md),
    choices(Strikers, St),
    % buy exactly one goalkeeper
    sum(Gk, #=, 1),
    % buy at least two defenders
    sum(Df, #>=, 2),
    % buy at least three midfielders
    sum(Md, #>=, 3),
    % buy at least two strikers
    sum(St, #>=, 2),
    % the players, strikers first, with their prices in the same order
    append([St, Md, Df, Gk], Vars),
    % buy at least eleven players in total
    sum(Vars, #>=, 11),
    % the total price stays within GBP 30 million (30000 thousands)
    append([Strikers, Midfielders, Defenders, Goalkeepers], Prices),
    scalar_product(Prices, Vars, #=, Cost),
    Cost #=< 30000.

choices(Prices, Xs) :-
    length(Prices, N),
    length(Xs, N),
    Xs ins 0..1.

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
