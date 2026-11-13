% twelve_pack: an ECLiPSe model from DCP Rosetta.
%
% Given a target number of items, find the combination of packs of different sizes whose total number of items is
% at least the target and as close to it as possible.
%
% Save this file as model.ecl. Download `twelve_pack.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/twelve_pack.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py twelve_pack.json
%   eclipse -b model.ecl -e "run('twelve_pack_1.dat'), halt"

% Data fields: target (the target number of items), packs (the number of items in each pack size, a list indexed
% from 0). Output counts: counts[I] is the number of packs of size packs[I] used.
:- lib(ic).

model(Instance, Counts, [counts-Counts], min(Items)) :-
    memberchk(target-Target, Instance),
    memberchk(packs-Packs, Instance),
    length(Packs, K),                      % the number of pack sizes
    length(Counts, K),
    Counts :: 0..Target,                   % the number of packs of each size
    % the packs used hold a total number of items
    Items #= Packs * Counts,
    % the total number of items is at least the target
    Items #>= Target.
    % the objective, Items, is minimised: the total is as close to the target as possible

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
