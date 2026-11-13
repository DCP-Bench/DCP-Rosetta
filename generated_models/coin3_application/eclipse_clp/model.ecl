% coin3_application: an ECLiPSe model from DCP Rosetta.
%
% Find the minimum number of coins that allows one to pay exactly any amount smaller than a given maximum amount, using
% a given set of denominations.
%
% Save this file as model.ecl. Download `coin3_application.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/coin3_application.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py coin3_application.json
%   eclipse -b model.ecl -e "run('coin3_application_1.dat'), halt"
%
% Data fields: denominations is the value of each coin type (a list indexed from 0 as in the JSON);
% max_amount_to_pay is the maximum amount, every amount below it must be payable.
:- lib(ic).
:- lib(listut).
:- lib(branch_and_bound).

% Outputs: x (the number of coins of each denomination).
model(Instance, Vars, [x-Xs], min(Total)) :-
    memberchk(denominations-Ds, Instance),
    memberchk(max_amount_to_pay-Max, Instance),
    length(Ds, N),
    length(Xs, N),
    Top is Max - 1,
    % no amount needs more coins of one denomination than fit in the top amount, so bound the count of each by it
    bounded(Xs, Ds, Top),
    % every amount from 1 up to the maximum amount minus one is paid exactly with the coins (Ys: coins used per amount)
    pay_all(1, Top, Ds, Xs, Ys),
    % the total number of coins is to be minimized
    Total #= sum(Xs),
    append(Xs, [Total | Ys], Vars).

% bounded(Xs, Ds, Top): each count is between 0 and Top divided by its denomination
bounded([], [], _).
bounded([X | Xs], [D | Ds], Top) :-
    Hi is Top // D,
    X :: 0..Hi,
    bounded(Xs, Ds, Top).

% pay_all(V, Top, Ds, Xs, Vars): every amount V..Top is paid with at most Xs coins of each denomination Ds
pay_all(V, Top, _, _, []) :-
    V > Top, !.
pay_all(V, Top, Ds, Xs, Vars) :-
    length(Ds, N),
    length(Ys, N),
    Ys :: 0..Top,
    within(Ys, Xs),
    Ds * Ys #= V,
    V1 is V + 1,
    pay_all(V1, Top, Ds, Xs, Rest),
    append(Ys, Rest, Vars).

% within(Ys, Xs): each entry of Ys is at most the matching entry of Xs
within([], []).
within([Y | Ys], [X | Xs]) :-
    Y #=< X,
    within(Ys, Xs).

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
