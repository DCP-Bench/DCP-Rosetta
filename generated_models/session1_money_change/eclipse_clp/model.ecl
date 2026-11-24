% session1_money_change: an ECLiPSe model from DCP Rosetta.
%
% Alice has to give Bob some change. She has different types of coins of different values and she has a certain number
% of coins of each value available. How can the change be composed with the available coins minimizing the number of
% coins used?
%
% Save this file as model.ecl. Download `session1_money_change.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_money_change.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py session1_money_change.json
%   eclipse -b model.ecl -e "run('session1_money_change_1.dat'), halt"
%
% The data fields: amount is the change to give; types_of_coins holds the value of each type of coin, and
% available_coins the number of coins of each type that Alice has. Both lists are indexed from 0 as in the JSON.

:- lib(ic).

% Output coin_counts: the number of coins of each type to give to Bob.
model(Instance, Counts, [coin_counts-Counts], min(sum(Counts))) :-
    memberchk(amount-Amount, Instance),
    memberchk(types_of_coins-Values, Instance),
    memberchk(available_coins-Available, Instance),
    length(Values, NTypes),
    length(Counts, NTypes),

    % Alice gives no more coins of a type than she has of it
    ( foreach(Count, Counts), foreach(Avail, Available) do
        Count #:: 0..Avail
    ),

    % the coins given to Bob are worth the amount of the change
    Values * Counts #= Amount.

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
