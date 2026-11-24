% cell_tower: a SWI-Prolog model from DCP Rosetta.
%
% A telecom company chooses which of several potential cell tower sites to build, with a limited budget, so as to
% cover the largest possible population. Each site has a build cost and reaches some of the regions of the city, and
% each region has a known population. A region is covered exactly when a built tower reaches it. Maximise the total
% population covered, with the total cost of the towers built within the budget.
%
% Save this file as model.pl. Download `cell_tower.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/cell_tower.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('cell_tower.json')" -t halt model.pl
%
% Data fields: budget (the total budget for towers), cost (the cost of building each site), delta (a matrix indexed
% from 0: row S is site S, column R is region R, and the entry is 1 when a tower on site S reaches region R),
% population (the population of each region). Lists are indexed from 0.
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(yall)).

model(Instance, Vars, [build_tower-Build, total_population_covered-Total], max(Total)) :-
    Delta = Instance.delta,
    Cost = Instance.cost,
    Population = Instance.population,
    Budget = Instance.budget,
    length(Cost, Sites),                   % the number of potential sites
    length(Population, Regions),           % the number of regions
    length(Build, Sites),
    Build ins 0..1,                        % Build[S] = 1 when a tower is built on site S
    length(Covered, Regions),
    Covered ins 0..1,                      % Covered[R] = 1 when region R is covered
    % the towers built cost no more than the budget
    scalar_product(Cost, Build, #=<, Budget),
    % a region is covered exactly when some built tower reaches it
    transpose(Delta, ByRegion),            % ByRegion[R] lists, for each site, whether it reaches region R
    maplist({Build}/[Reaches, C]>>covered_by(Build, Reaches, C), ByRegion, Covered),
    % the total population covered, to be maximised
    scalar_product(Population, Covered, #=, Total),
    append([[Total], Build, Covered], Vars).

% region C is covered only if a built site reaches it, and a built site that reaches it covers it
covered_by(Build, Reaches, C) :-
    scalar_product(Reaches, Build, #>=, C),
    maplist({C}/[B, R]>>(B * R #=< C), Build, Reaches).

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
