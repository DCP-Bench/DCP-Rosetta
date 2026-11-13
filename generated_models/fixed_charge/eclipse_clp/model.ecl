% fixed_charge: an ECLiPSe model from DCP Rosetta.
%
% A company manufactures shirts, shorts and pants. Each product requires a number of hours of labor and a certain amount
% of cloth, and the company has a limited capacity of both. In addition, all of these products can be manufactured only
% by renting an appropriate machine, each product having its own machine type. The renting cost of a machine is paid
% once, however much is made on it. The profit on the products (excluding the cost of renting the equipment) is also
% known, per unit, and each product is made in a whole number of units. The company would like to maximize its profit:
% the profit on the units made, less the cost of the machines rented.
%
% Save this file as model.ecl. Download `fixed_charge.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/fixed_charge.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py fixed_charge.json
%   eclipse -b model.ecl -e "run('fixed_charge_1.dat'), halt"
%
% The data fields: product[p] is the row of product p whose first entry is its profit per unit; use[p][r] is the amount
% of resource r (0 is labor, 1 is cloth) that one unit of product p needs; capacity[r] is the capacity of resource r;
% renting_cost[m] is the renting cost of machine m; shirtM, shortM and pantM are the machines of the shirts, shorts and
% pants; max_production is the largest number of units of a product.

:- lib(ic).
:- lib(listut).

% Make[p] is the number of units of product p (shirts, shorts, pants); Rent[m] is 1 when machine m is rented.
model(Instance, Vars, [z-Z], max(Z)) :-
    memberchk(product-ProductRows, Instance),
    memberchk(use-UseRows, Instance),
    memberchk(capacity-Capacity, Instance),
    memberchk(renting_cost-RentCosts, Instance),
    memberchk(max_production-MaxP, Instance),
    memberchk(shirtM-ShirtM, Instance),
    memberchk(shortM-ShortM, Instance),
    memberchk(pantM-PantM, Instance),
    length(ProductRows, NP),
    length(Make, NP),
    Make :: 0..MaxP,
    length(RentCosts, NM),
    length(Rent, NM),
    Rent :: 0..1,
    Machines = [ShirtM, ShortM, PantM],

    % the products made use no more labor and no more cloth than the capacity of each
    length(Capacity, NR),
    ( for(R, 0, NR-1), param(UseRows, Make, Capacity) do
        ( foreach(Row, UseRows), foreach(X, Make), foreach(T, Terms), param(R) do
            nth0(R, Row, U),
            T #= U * X
        ),
        nth0(R, Capacity, Cap),
        sum(Terms) #=< Cap
    ),

    % a product can be made only on its machine, and only when that machine is rented
    ( foreach(X, Make), foreach(M, Machines), param(Rent, MaxP) do
        nth0(M, Rent, Rented),
        X #=< MaxP * Rented
    ),

    % the profit on the units made, per product
    ( foreach(Row, ProductRows), foreach(X, Make), foreach(T, ProfitTerms) do
        Row = [Profit | _],
        T #= Profit * X
    ),

    % the cost of renting the machines, each paid once
    ( foreach(C, RentCosts), foreach(R, Rent), foreach(T, CostTerms) do
        T #= C * R
    ),

    % z is the profit on the units made less the renting cost of the machines
    Z #= sum(ProfitTerms) - sum(CostTerms),

    append(Make, Rent, Vars).

% Reads the data file, builds the model, solves it and prints each output.
run(File) :-
    open(File, read, Stream), read(Stream, Instance), close(Stream),
    solve_model(Instance).

:- lib(branch_and_bound).

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
