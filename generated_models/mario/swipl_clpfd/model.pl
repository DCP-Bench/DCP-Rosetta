% mario: a SWI-Prolog model from DCP Rosetta.
%
% Mario needs to collect as much gold as possible by visiting different houses. He starts at Mario's house and ends
% at Luigi's house, and the route returns from Luigi's house to Mario's house. Each house has a certain amount of
% gold, and the travel between houses consumes fuel. Mario has a limited amount of fuel, and he needs to plan his
% route to maximize the gold collected without exceeding the fuel limit.
%
% Save this file as model.pl. Download `mario.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/mario.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('mario.json')" -t halt model.pl
%
% Data fields: nHouses (the number of houses, numbered from 0), marioHouse and luigiHouse (the houses of Mario and
% Luigi), fuelLimit (the fuel Mario has), goldInHouse (the gold lying in each house), arc_fuel (arc_fuel[I][J] is the
% fuel burnt on the travel from house I to house J).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).
:- use_module(library(http/json)).

model(Instance, Succ-Order-OnRoutes, [s-Succ], max(Gold)) :-
    N = Instance.nHouses,
    Mario = Instance.marioHouse,
    Luigi = Instance.luigiHouse,
    FuelLimit = Instance.fuelLimit,
    GoldInHouse = Instance.goldInHouse,
    ArcFuel = Instance.arc_fuel,
    Last is N - 1,
    numlist(0, Last, Houses),
    append(ArcFuel, FuelArcs),             % the fuel of the travel from I to J is FuelArcs[I*N + J]

    % Succ[I] is the house after house I on the route; a house off the route is its own successor
    length(Succ, N),
    Succ ins 0..Last,
    % each house is the successor of at most one house, so the route cannot branch
    all_distinct(Succ),
    % the route ends at Luigi's house and returns to Mario's house
    nth0(Luigi, Succ, LuigiNext),
    LuigiNext #= Mario,

    % Order[I] is the position of house I on the route, Mario's house being first
    length(Order, N),
    Order ins 1..N,
    all_distinct(Order),
    nth0(Mario, Order, 1),
    % a house on the route is followed by the house one position later, except that the
    % route returns to Mario's house from Luigi's house; so no loop avoids Mario's house
    maplist(order_step(Order, Mario), Houses, Succ, Order),

    % OnRoutes[I] is 1 when house I is on the route, 0 when it is off the route
    length(OnRoutes, N),
    OnRoutes ins 0..1,
    maplist(on_route, Succ, Houses, OnRoutes),

    % the fuel burnt over the legs of the route stays within the limit
    maplist(leg_fuel(FuelArcs, N, Mario), Houses, Succ, OnRoutes, Fuels),
    sum(Fuels, #=<, FuelLimit),

    % the gold collected is the gold of the houses on the route
    sum_list(GoldInHouse, MaxGold),
    Gold in 0..MaxGold,
    scalar_product(GoldInHouse, OnRoutes, #=, Gold).

% on_route(+Next, +House, -OnRoute): a house is on the route unless it is its own successor
on_route(Next, House, OnRoute) :-
    OnRoute #<==> (Next #\= House).

% order_step(+Order, +Mario, +House, +Next, +Rank): when House is on the route and Next is not Mario's house, Next
% comes one position after House
order_step(Order, Mario, House, Next, Rank) :-
    Index #= Next + 1,
    element(Index, Order, NextRank),
    (Next #\= House #/\ Next #\= Mario) #==> (NextRank #= Rank + 1).

% leg_fuel(+FuelArcs, +N, +Mario, +House, +Next, +OnRoute, -Fuel): the fuel of the leg from House to Next, 0 off the
% route, and 0 for the return leg into Mario's house, which is not part of the fuel Mario burns on the run
leg_fuel(FuelArcs, N, Mario, House, Next, OnRoute, Fuel) :-
    Index #= House * N + Next + 1,
    element(Index, FuelArcs, Cost),
    Outward #<==> (Next #\= Mario),
    Fuel #= OnRoute * Outward * Cost.

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
