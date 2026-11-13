% session2_subset_sum: an ECLiPSe model from DCP Rosetta.
%
% A bank van had several bags of coins, each bag holding a number of coins of one of the kinds given (there are
% several bags of each kind). While the van was parked on the street, thieves stole some of the bags, and a
% given total number of coins was lost. Find how many bags were stolen of each kind.
%
% Save this file as model.ecl. Download `session2_subset_sum.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subset_sum.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py session2_subset_sum.json
%   eclipse -b model.ecl -e "run('session2_subset_sum_1.dat'), halt"

% coin_numbers: the number of coins in a bag of each kind, indexed from 0 as in the JSON.
% total_coins_lost: the total number of coins lost.

:- lib(ic).

% Bags: the number of bags stolen of each kind, in the order of the coin numbers.
model(Instance, Bags, [bags-Bags]) :-
    memberchk(coin_numbers-Coins, Instance),
    memberchk(total_coins_lost-Total, Instance),
    length(Coins, K),                    % the number of kinds of coin bag
    length(Bags, K),
    Bags :: 0..Total,                    % any number of bags of a kind may have been stolen (at most Total, a bag holds a coin)
    % the coins in the stolen bags add up to the total lost
    Total #= Coins * Bags.

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
