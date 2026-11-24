% diet: a SWI-Prolog model from DCP Rosetta.
%
% Given the prices and the nutritional requirements (at least) for each nutrition type, what is the optimal diet?
% The optimal diet is to minimize the cost of the products, each food bought in a whole number of units:
%
%   Type of food                    Calories  Chocolate (ounces)  Sugar (ounces)  Fat (ounces)
%   Chocolate Cake (1 slice)             400                   3               2             2
%   Chocolate ice cream (1 scoop)        200                   2               2             4
%   Cola (1 bottle)                      150                   0               4             1
%   Pineapple cheesecake (1 piece)       500                   0               4             5
%
% Save this file as model.pl. Download `diet.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/diet.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('diet.json')" -t halt model.pl
%
% Data fields: n (the number of foods), price (the price of one unit of each food, in the order of the table),
% limits (the least amount required of each nutrition type: calories, chocolate, sugar, fat), lists indexed from 0.
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(yall)).

model(Instance, Vars, [cost-Cost], min(Cost)) :-
    N = Instance.n,                    % the number of foods
    Price = Instance.price,            % the price of one unit of each food
    Limits = Instance.limits,          % the least amount required of each nutrition type
    length(Units, N),                  % Units[F] is the whole number of units of food F bought
    max_list(Limits, MostNeeded),
    % no optimal diet buys a food in more units than the largest limit, as every nutrition type a unit supplies, it supplies at least 1 of
    Units ins 0..MostNeeded,
    nutrition(Table),
    % every nutrition type reaches at least its required amount
    maplist({Units}/[Row, Limit]>>scalar_product(Row, Units, #>=, Limit), Table, Limits),
    % the cost of the diet is the price of every unit bought
    scalar_product(Price, Units, #=, Cost),
    Vars = [Cost|Units].

% Table[T][F] is the amount of nutrition type T in one unit of food F, rows in the order calories, chocolate, sugar, fat.
nutrition([[400, 200, 150, 500],
           [3, 2, 0, 0],
           [2, 2, 4, 4],
           [2, 4, 1, 5]]).

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
