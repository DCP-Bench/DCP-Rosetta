% cutting_stock: a SWI-Prolog model from DCP Rosetta.
%
% This is a cutting stock problem. Raw rolls have a width roll_width, and pieces of several smaller widths are cut
% from them: orders[i] pieces of width widths[i] are needed. There are num_patterns cutting patterns, and cutting one
% raw roll with pattern i yields num_rolls_width[i][j] pieces of width widths[j]. The problem aims to minimize the
% total number of raw rolls cut, while at least the ordered number of pieces of each width is produced. How many rolls
% should be cut using each pattern?
%
% Save this file as model.pl. Download `cutting_stock.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/cutting_stock.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('cutting_stock.json')" -t halt model.pl
%
% Data fields: num_patterns (the number of cutting patterns), num_rolls_width (the pieces of each width that one roll
% cut with each pattern yields: a list of rows indexed from 0, one per pattern, each holding the count for each width
% indexed from 0), orders (the number of pieces of each width ordered, indexed from 0).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(yall)).
:- use_module(library(lists)).

model(Instance, [Total|Used], [patterns_used-Used, min_rolls_cut-Total], min(Total)) :-
    NumPatterns = Instance.num_patterns,
    Yields = Instance.num_rolls_width,
    Orders = Instance.orders,
    % Used[I] is the number of rolls cut with pattern I
    length(Used, NumPatterns),
    sum_list(Orders, Most),                % a bound on any count, not in the statement: an optimum never needs more rolls than pieces ordered
    Used ins 0..Most,
    % for each width, the pieces yielded by all the rolls are at least the number ordered
    transpose(Yields, Columns),
    maplist({Used}/[Column, Order]>>scalar_product(Column, Used, #>=, Order), Columns, Orders),
    % the total number of raw rolls cut: minimised
    sum(Used, #=, Total).

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
