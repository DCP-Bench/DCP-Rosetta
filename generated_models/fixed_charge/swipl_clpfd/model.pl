% fixed_charge: a SWI-Prolog model from DCP Rosetta.
%
% A company manufactures shirts, shorts and pants. Each product needs a number of hours of labour and an amount of
% cloth, and the company has a limited capacity of each resource. Every product can be made only on its own machine
% type, which the company rents: the renting cost of a machine is paid once, however much is made on it. Each product
% has a profit per unit (excluding the cost of renting machines), and each product is made in a whole number of units.
% The company wants to maximise its profit: the profit on the units made, less the cost of the machines rented.
% Give the maximum profit that the company can make.
%
% Save this file as model.pl. Download `fixed_charge.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/fixed_charge.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('fixed_charge.json')" -t halt model.pl
%
% Data fields: product (one pair per product: the profit per unit of that product, then its product id), use (one
% list per product, indexed from 0, giving the amount of each resource it needs per unit, in resource order),
% capacity (the capacity of each resource, indexed from 0), machines (the machine each product is made on, indexed
% from 0), renting_cost (the cost of renting each machine, indexed from 0) and max_production (the most units of any
% one product). The model reads only these fields.
:- use_module(library(clpfd)).

model(Instance, [X, Y, Revenue, Rent], [z-Z], max(Z)) :-
    firsts(Instance.product, Profits),   % Profits[P]: profit per unit of product P
    Use = Instance.use,
    Capacity = Instance.capacity,
    Machines = Instance.machines,        % Machines[P]: the machine product P is made on
    RentCosts = Instance.renting_cost,
    Max = Instance.max_production,
    length(Machines, NP),
    length(X, NP),
    X ins 0..Max,                        % units made of each product
    length(RentCosts, NM),
    length(Y, NM),
    Y ins 0..1,                          % 1 when the machine is rented
    % the resources used by all products fit within their capacities
    transpose(Use, UseByResource),
    maplist(fits_capacity(X), UseByResource, Capacity),
    % a product can be made only when its machine is rented
    maplist(needs_machine(Y, Max), X, Machines),
    % profit on the units made, less the cost of the machines rented
    scalar_product(Profits, X, #=, Revenue),
    scalar_product(RentCosts, Y, #=, Rent),
    Z #= Revenue - Rent.

firsts([], []).
firsts([[P|_]|Rest], [P|Ps]) :-
    firsts(Rest, Ps).

fits_capacity(X, Coefficients, Cap) :-
    scalar_product(Coefficients, X, #=<, Cap).

needs_machine(Y, Max, Units, Machine) :-
    nth0(Machine, Y, Rented),
    Units #=< Max * Rented.

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
