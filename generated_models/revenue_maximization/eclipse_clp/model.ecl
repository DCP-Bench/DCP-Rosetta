% revenue_maximization: an ECLiPSe model from DCP Rosetta.
%
% We have a set of flight legs (one-way non-stop flights), each with a limited passenger capacity. According to market
% research, a set of flight itineraries is sold as a package with a given price, and each package has an estimated
% demand. How many units of each package should we sell to maximize the revenue? We reserve the passenger seats
% according to the number of packages we want to sell.
%
% Save this file as model.ecl. Download `revenue_maximization.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/revenue_maximization.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py revenue_maximization.json
%   eclipse -b model.ecl -e "run('revenue_maximization_1.dat'), halt"
%
% The data fields: available_seats is the seat capacity of each flight leg; delta holds, for each package (one row
% per package), the number of seats it reserves on each leg; demand is the estimated demand of each package; revenue
% is the price of one unit of each package. All lists are indexed from 0 as in the JSON.

:- lib(ic).
:- lib(listut).

% Outputs: max_revenue is the total revenue, packages_to_sell the number of units of each package to sell.
model(Instance, Xs, [max_revenue-Revenue, packages_to_sell-Xs], max(Revenue)) :-
    memberchk(available_seats-Seats, Instance),
    memberchk(delta-Delta, Instance),
    memberchk(demand-Demand, Instance),
    memberchk(revenue-Price, Instance),
    length(Demand, NPackages),
    length(Seats, NLegs),
    length(Xs, NPackages),

    % the units of each package sold do not exceed its estimated demand
    ( foreach(X, Xs), foreach(D, Demand) do
        X #:: 0..D
    ),

    % the seats reserved on each leg by the packages sold do not exceed the seats of that leg
    ( for(Leg, 1, NLegs), param(Seats, Delta, Xs) do
        nth1(Leg, Seats, Capacity),
        ( foreach(Row, Delta), param(Leg), foreach(Reserved, Column) do
            nth1(Leg, Row, Reserved)
        ),
        Column * Xs #=< Capacity
    ),

    % the total revenue is the price of each package times the units sold
    Revenue #= Price * Xs.

:- lib(branch_and_bound).

% Reads the data file, builds the model, solves it and prints each output.
run(File) :-
    open(File, read, Stream), read(Stream, Instance), close(Stream),
    solve_model(Instance).

solve_model(Instance) :-
    (   current_module(gfd) -> Lib = gfd ; Lib = ic ),
    (   current_predicate(model/4)
    ->  model(Instance, Vars, Outputs, Objective)
    ;   model(Instance, Vars, Outputs), Objective = none
    ),
    (   Objective = max(Expr)
    ->  call(Lib:(Total #= Expr)), call(Lib:(Cost #= -Total)),
        minimize(run_search(Vars, Outputs), Cost)
    ;   Objective = min(Expr)
    ->  call(Lib:(Cost #= Expr)),
        minimize(run_search(Vars, Outputs), Cost)
    ;   run_search(Vars, Outputs)
    ),
    ( foreach(Name-Value, Outputs) do printf("%w = %w%n", [Name, Value]) ).

run_search(Vars, Outputs) :-
    (   current_predicate(search_goal/1) -> search_goal(Vars) ; labeling(Vars) ),
    term_variables(Outputs, Free),
    labeling(Free).
