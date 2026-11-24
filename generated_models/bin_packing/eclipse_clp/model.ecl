% bin_packing: an ECLiPSe model from DCP Rosetta.
%
% Given several items of specific weights and a number of bins of a fixed capacity, assign each item to a bin so
% that the total weight of the items in each bin does not exceed the capacity.
%
% Save this file as model.ecl. Download `bin_packing.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/bin_packing.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py bin_packing.json
%   eclipse -b model.ecl -e "run('bin_packing_1.dat'), halt"

% Instance fields: weights (the weight of each item, a list indexed from 0), capacity (the capacity of each bin),
% num_bins (the number of bins). Bins is the output: Bins[I] is the 0-based bin that item I is assigned to.
:- lib(ic).
:- lib(ic_global).

model(Instance, Bins1, [bins-Bins]) :-
    memberchk(weights-Weights, Instance),
    memberchk(capacity-Capacity, Instance),
    memberchk(num_bins-NumBins, Instance),
    length(Weights, N),                    % the number of items
    length(Bins1, N),
    length(Bins, N),
    % each item is assigned to one of the bins (numbered from 1 inside the model, shifted to 0-based for the output)
    Bins1 :: 1..NumBins,
    ( foreach(B1, Bins1), foreach(B, Bins) do B #= B1 - 1 ),
    % the total weight of the items in each bin does not exceed the capacity
    length(Loads, NumBins),
    Loads :: 0..Capacity,
    bin_packing(Bins1, Weights, Loads).

% the search picks the item with the fewest candidate bins first and tries the lowest bin first
search_goal(Bins1) :-
    search(Bins1, 0, first_fail, indomain_min, complete, []).

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
