% csplib_041_n_fractions: an ECLiPSe model from DCP Rosetta.
%
% Find distinct non-zero digits such that A / BC + D / EF + G / HI = 1, where BC, EF and HI are the two-digit numbers
% formed by B and C, E and F, and H and I, respectively.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_041_n_fractions.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

:- lib(ic).
:- lib(branch_and_bound).

% Outputs the nine digits A to I, each a non-zero digit, all different.
model(_Instance, Vars, ['A'-A, 'B'-B, 'C'-C, 'D'-D, 'E'-E, 'F'-F, 'G'-G, 'H'-H, 'I'-I]) :-
    Vars = [A, B, C, D, E, F, G, H, I],
    Vars :: 1..9,
    % the nine digits are all different
    alldifferent(Vars),

    % the two-digit numbers BC, EF and HI
    BC #= 10 * B + C,
    EF #= 10 * E + F,
    HI #= 10 * H + I,

    % A / BC + D / EF + G / HI = 1, multiplied through by BC * EF * HI
    EFHI #= EF * HI,
    BCHI #= BC * HI,
    BCEF #= BC * EF,
    BCEFHI #= BCEF * HI,
    A * EFHI + D * BCHI + G * BCEF #= BCEFHI.

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
