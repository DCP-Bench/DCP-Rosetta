% best_host: an ECLiPSe model from DCP Rosetta.
%
% Six dinner guests sit around a round table. Some guests do not get along: two guests who do not get along and sit next
% to each other create conflict. Andrew will only sit next to Dave and Frank; Betty only next to Cara and Erica; Cara only
% next to Betty and Frank; Dave only next to Andrew and Erica; Erica only next to Betty and Dave; Frank only next to Andrew
% and Cara. Arrange the guests in a seating order around the table so that there is no conflict at dinner.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/best_host.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

:- lib(ic).

% The guests are numbered 0 Andrew, 1 Betty, 2 Cara, 3 Dave, 4 Erica, 5 Frank.
% Row 6*A + B of the table is 1 when guest A may sit next to guest B, and 0 otherwise.
friend_table([
    0,0,0,1,0,1,    % Andrew sits next to Dave and Frank only
    0,0,1,0,1,0,    % Betty sits next to Cara and Erica only
    0,1,0,0,0,1,    % Cara sits next to Betty and Frank only
    1,0,0,0,1,0,    % Dave sits next to Andrew and Erica only
    0,1,0,1,0,0,    % Erica sits next to Betty and Dave only
    1,0,1,0,0,0     % Frank sits next to Andrew and Cara only
]).

% two guests sitting next to each other do not conflict when the table allows the pair
neighbours_ok(A, B, Table) :-
    Index #= 6 * A + B + 1,
    element(Index, Table, 1).

% Output x: the guest in each seat, going around the table.
model(_Instance, Xs, [x-Xs]) :-
    length(Xs, 6),
    Xs :: 0..5,
    % each guest sits exactly once
    alldifferent(Xs),
    friend_table(Table),
    % the table is round: each seat is next to the following one, and the last seat is next to the first
    Xs = [X1, X2, X3, X4, X5, X6],
    neighbours_ok(X1, X2, Table),
    neighbours_ok(X2, X3, Table),
    neighbours_ok(X3, X4, Table),
    neighbours_ok(X4, X5, Table),
    neighbours_ok(X5, X6, Table),
    neighbours_ok(X6, X1, Table).

:- lib(branch_and_bound).

% Builds the model, solves it and prints each output.
run :- solve_model([]).

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
