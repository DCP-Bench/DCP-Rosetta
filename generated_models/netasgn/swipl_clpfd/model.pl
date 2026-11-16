% netasgn: a SWI-Prolog model from DCP Rosetta.
%
% Consider a project assignment problem. Given a set of people and a set of projects. Each person has a certain number
% of available hours, and each project requires a certain number of hours. The cost per hour of work for a person on a
% project is given, and each person can contribute to a project up to a maximum limit of hours. Minimize the total
% cost of assigning people to projects. The total number of hours assigned from each person equals its supply, and the
% total number of hours assigned to each project equals its demand. Decide how many hours each person is assigned to
% each project.
%
% Save this file as model.pl. Download `netasgn.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/netasgn.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('netasgn.json')" -t halt model.pl
%
% Data fields: supply (the hours available from each person), demand (the hours required by each project), cost[I][J]
% (the cost per hour of person I on project J), limit[I][J] (the most hours person I may work on project J). Lists are
% indexed from 0.
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).
:- use_module(library(http/json)).

model(Instance, Flat, [assign-Rows, total_cost-TotalCost], min(TotalCost)) :-
    Supply = Instance.supply,
    Demand = Instance.demand,
    Cost = Instance.cost,
    Limit = Instance.limit,
    length(Supply, People),
    length(Demand, Projects),
    % Rows[I][J] is the hours person I works on project J; no person works more than the total supply
    sum_list(Supply, MaxHours),
    length(Rows, People),
    maplist({Projects, MaxHours}/[Row]>>(length(Row, Projects), Row ins 0..MaxHours), Rows),
    append(Rows, Flat),
    % a person works no more hours on a project than the limit for that pair
    maplist(within_limit, Rows, Limit),
    % each person's hours add up to the supply of that person
    maplist(hours_total, Rows, Supply),
    % each project's hours add up to the demand of that project
    transpose(Rows, Columns),
    maplist(hours_total, Columns, Demand),
    % the total cost of the hours worked
    maplist(row_cost, Rows, Cost, RowCosts),
    sum(RowCosts, #=, TotalCost).

% within_limit(+Hours, +Limits): the hours on each project are at most the limit for that project
within_limit(Hours, Limits) :-
    maplist([H, Cap]>>(H #=< Cap), Hours, Limits).

% hours_total(+Hours, +Total): the hours add up to the total
hours_total(Hours, Total) :-
    sum(Hours, #=, Total).

% row_cost(+Hours, +Prices, -Spent): the cost of the hours one person works
row_cost(Hours, Prices, Spent) :-
    scalar_product(Prices, Hours, #=, Spent).

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
