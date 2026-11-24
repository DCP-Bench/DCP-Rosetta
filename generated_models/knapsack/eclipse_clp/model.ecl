% knapsack: an ECLiPSe model from DCP Rosetta.
%
% A hiker is planning a trip and needs to decide which items to take in their backpack. Each item has a certain value
% and weight, and the hiker wants to maximize the total value of the items in the backpack without exceeding the weight
% capacity of the backpack.
%
% Save this file as model.ecl. Download `knapsack.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py knapsack.json
%   eclipse -b model.ecl -e "run('knapsack_1.dat'), halt"
%
% The instance fields: capacity is the weight capacity of the backpack; values and weights are lists of the value
% and the weight of each item, indexed from 0 as in the JSON.

:- lib(ic).
:- lib(branch_and_bound).

% Output x: one 0/1 flag per item, 1 when the item is taken.
model(Instance, Xs, [x-Xs], max(sum(Gains))) :-
    memberchk(capacity-Capacity, Instance),
    memberchk(values-Values, Instance),
    memberchk(weights-Weights, Instance),
    length(Values, N),
    length(Xs, N),

    % each item is either taken (1) or left out (0)
    Xs :: 0..1,

    % the weight carried for each item is its weight if the item is taken, 0 otherwise
    ( foreach(W, Weights), foreach(X, Xs), foreach(Carried, CarriedWeights) do
        Carried #= W * X
    ),

    % without exceeding the weight capacity of the backpack
    sum(CarriedWeights) #=< Capacity,

    % the value gained from each item is its value if the item is taken, 0 otherwise
    ( foreach(V, Values), foreach(X, Xs), foreach(Gain, Gains) do
        Gain #= V * X
    ).

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
