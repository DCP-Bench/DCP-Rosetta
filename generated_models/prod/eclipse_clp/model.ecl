% prod: an ECLiPSe model from DCP Rosetta.
%
% A production problem with a set of products. Each product j has a quantity limit u[j], a profit per unit c[j] and a
% resource use a[j] per unit, and there is a total resource amount b. The goal is to choose the production quantity of
% each product so that the total profit is as large as possible, while the sum of the quantity of each product divided
% by its resource use a[j] stays at most b, and each quantity lies between 0 and its limit u[j].
%
% Save this file as model.ecl. Download `prod.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/prod.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py prod.json
%   eclipse -b model.ecl -e "run('prod_1.dat'), halt"
%
% The data fields: a[j] is the resource use per unit of product j, b is the total amount of resource, c[j] is the
% profit per unit of product j, and u[j] is the limit on the quantity of product j. The lists are indexed from 0 as
% in the JSON.

:- lib(ic).
:- lib(branch_and_bound).

% Outputs: x[j] is the production quantity of product j; total_profit is the total profit.
model(Instance, Vars, [total_profit-Profit, x-Xs], max(Profit)) :-
    memberchk(a-As, Instance),
    memberchk(b-B, Instance),
    memberchk(c-Cs, Instance),
    memberchk(u-Us, Instance),
    length(As, NumProducts),
    length(Xs, NumProducts),
    ( foreach(X, Xs), foreach(U, Us) do
        X :: 0..U
    ),

    % the resource used, sum of X[j]/a[j], is at most b; multiplied by the lcm L of the a[j], each coefficient is L/a[j]
    lcm_of(As, L),
    ( foreach(A, As), foreach(Coef, Coefs), param(L) do
        Coef is L // A
    ),
    ( foreach(K, Coefs), foreach(X, Xs), foreach(Use, Uses) do
        Use #= K * X
    ),
    Capacity is L * B,
    sum(Uses) #=< Capacity,

    % the total profit is the sum of c[j] * X[j], which is to be as large as possible
    ( foreach(C, Cs), foreach(X, Xs), foreach(Gain, Gains) do
        Gain #= C * X
    ),
    Profit #= sum(Gains),

    Vars = Xs.

% the least common multiple of a list of positive numbers
lcm_of([], 1).
lcm_of([A | As], L) :-
    lcm_of(As, L0),
    gcd_of(A, L0, G),
    L is A * L0 // G.

% the greatest common divisor of two positive numbers
gcd_of(A, B, A) :-
    B =:= 0,
    !.
gcd_of(A, B, G) :-
    R is A mod B,
    gcd_of(B, R, G).

% the search picks the variable with the fewest candidate values first and tries the lowest value first
search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

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
