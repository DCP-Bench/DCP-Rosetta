% csplib_034_warehouse_location: an ECLiPSe model from DCP Rosetta.
%
% A company must decide which warehouses to open from a set of candidate locations to supply a set of stores. Each
% warehouse has a fixed maintenance cost and a capacity limiting the number of stores it can supply. Each store must be
% supplied by exactly one open warehouse, and there is a supply cost that varies with the store and the warehouse.
% Minimise the total cost: the maintenance costs of the opened warehouses plus the supply costs of all stores.
%
% Save this file as model.ecl. Download `csplib_034_warehouse_location.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_034_warehouse_location.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_034_warehouse_location.json
%   eclipse -b model.ecl -e "run('csplib_034_warehouse_location_1.dat'), halt"
%
% The instance fields: building_cost (the maintenance cost of an open warehouse), capacity (the number of stores each
% warehouse can supply, indexed from 0), cost_matrix (cost_matrix[S][W] is the supply cost of store S from warehouse W,
% both indexed from 0), n_stores (the number of stores), n_suppliers (the number of candidate warehouses).

:- lib(ic).
:- lib(branch_and_bound).
:- lib(listut).

% Outputs: total_cost (the minimised cost), open_warehouses (1 when the warehouse is open, indexed from 0) and
% supplier_assignment (the warehouse of each store, indexed from 0).
model(Instance, Vars, [total_cost-Total, open_warehouses-Open, supplier_assignment-Assign], min(Total)) :-
    memberchk(building_cost-Build, Instance),
    memberchk(capacity-Caps, Instance),
    memberchk(cost_matrix-Matrix, Instance),
    memberchk(n_stores-NS, Instance),
    memberchk(n_suppliers-NW, Instance),
    length(Open, NW),
    Open :: 0..1,
    length(Assign, NS),
    Assign :: 0..(NW - 1),
    % the 1-based warehouse index of each store, for use with element/3
    ( foreach(A, Assign), foreach(Ind, Inds) do Ind #= A + 1 ),

    % each store is supplied by an open warehouse
    ( foreach(Ind, Inds), param(Open) do element(Ind, Open, 1) ),

    % each warehouse supplies at most its capacity of stores
    ( for(W, 1, NW), param(Inds, Caps) do
        nth1(W, Caps, Cap),
        ( foreach(Ind, Inds), foreach(Bool, Bools), param(W) do Bool #= (Ind #= W) ),
        sum(Bools) #=< Cap
    ),

    % the supply cost of each store from its warehouse
    ( foreach(Ind, Inds), foreach(Row, Matrix), foreach(Cost, Costs) do element(Ind, Row, Cost) ),

    % the total cost: the maintenance cost of the open warehouses plus the supply costs of the stores
    Total #= Build * sum(Open) + sum(Costs),
    append(Assign, Open, Vars).

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
