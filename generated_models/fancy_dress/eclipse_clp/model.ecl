% fancy_dress: an ECLiPSe model from DCP Rosetta.
%
% Mr Greenfan's dress party requires the male guests to wear green. The rules: (1) a guest wearing a green tie
% must wear a green shirt; (2) a guest wearing green socks or a green shirt must also wear a green tie or a green
% hat; (3) a guest wearing a green shirt or a green hat, or not wearing green socks, must wear a green tie;
% (4) a guest not dressed according to rules 1 to 3 pays an $11 entrance fee. Mr Greenguest owns only a green
% shirt, which costs nothing to wear; he can buy a green tie for $10, a used green hat for $2 and green socks for
% $12. Find the cheapest choice of items for him to take part.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/fancy_dress.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

% The model reads no data. Each of T (tie), H (hat), R (shirt), S (socks) and N (entrance fee) is 1 when
% Mr Greenguest chooses that item, or pays the fee, and 0 otherwise.

:- lib(ic).

model(_Instance, [T, H, R, S, N], [t-T, h-H, r-R, s-S, n-N], min(Cost)) :-
    [T, H, R, S, N] :: 0..1,
    % rule 1: a green tie requires a green shirt
    Rule1 #= (T #=< R),
    % rule 2: green socks or a green shirt require a green tie or a green hat
    WearsSocksOrShirt #= (S + R #>= 1),
    WearsTieOrHat #= (T + H #>= 1),
    Rule2 #= (WearsSocksOrShirt #=< WearsTieOrHat),
    % rule 3: a green shirt, a green hat, or no green socks require a green tie
    WearsShirtOrHatOrNoSocks #= (R + H + (1 - S) #>= 1),
    Rule3 #= (WearsShirtOrHatOrNoSocks #=< T),
    % rule 4: the guest pays the entrance fee exactly when rules 1 to 3 are not all followed
    Followed #= (Rule1 + Rule2 + Rule3 #= 3),
    N #= 1 - Followed,
    % the cost: the tie $10, the hat $2, the socks $12 and the fee $11 (the owned shirt is free)
    Cost #= 10 * T + 2 * H + 12 * S + 11 * N.

:- lib(branch_and_bound).

% Builds the model, solves it and prints each output.
run :-
    solve_model([]).

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
