% revenue_maximization: a SWI-Prolog model from DCP Rosetta.
%
% A set of flight legs (one-way non-stop flights) has a limited passenger capacity. A set of flight itineraries is
% sold as packages, each at a given price, and each package has an estimated demand. How many units of each package
% should we sell to maximize the revenue? The passenger seats are reserved according to the number of packages sold.
%
% Save this file as model.pl. Download `revenue_maximization.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/revenue_maximization.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('revenue_maximization.json')" -t halt model.pl
%
% Data fields: available_seats (the seat capacity of each flight leg), delta (delta[P][L] is the number of seats
% package P uses on flight leg L), demand (the estimated demand for each package), revenue (the price of each
% package); lists indexed from 0.
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(yall)).

model(Instance, Sell, [packages_to_sell-Sell, max_revenue-Revenue], max(Revenue)) :-
    Seats = Instance.available_seats,
    Demand = Instance.demand,
    Price = Instance.revenue,
    Delta = Instance.delta,
    length(Demand, NumPackages),           % the number of packages
    length(Sell, NumPackages),             % Sell[P] is the number of units of package P sold
    % sell no more units of a package than its estimated demand
    maplist([S, D]>>(S in 0..D), Sell, Demand),
    % the seats used on each flight leg by the packages sold do not exceed the seats of that leg
    transpose(Delta, SeatsPerLeg),         % SeatsPerLeg[L] lists the seats each package uses on leg L
    maplist({Sell}/[Uses, Capacity]>>scalar_product(Uses, Sell, #=<, Capacity), SeatsPerLeg, Seats),
    % the revenue is the total price of the packages sold
    scalar_product(Price, Sell, #=, Revenue).

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
