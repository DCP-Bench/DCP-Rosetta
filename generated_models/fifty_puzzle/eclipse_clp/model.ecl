% fifty_puzzle: an ECLiPSe model from DCP Rosetta.
%
% A side show has a number of little dummies, each with a number on it. Take as many throws as you like at a
% cent apiece; each dummy knocked over stays down. Add up the numbers on the dummies you knock down, and when the
% sum amounts to exactly a given target sum, neither more nor less, you get a genuine prize. Find which dummies
% are knocked over.
%
% Save this file as model.ecl. Download `fifty_puzzle.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/fifty_puzzle.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py fifty_puzzle.json
%   eclipse -b model.ecl -e "run('fifty_puzzle_1.dat'), halt"

% Data fields: target_sum (the exact sum to reach), values (the number on each dummy, a list indexed from 0).

:- lib(ic).

model(Instance, Knocked, [dummies-Knocked]) :-
    memberchk(target_sum-Target, Instance),
    memberchk(values-Values, Instance),
    length(Values, N),
    length(Knocked, N),
    % each dummy is either knocked over (1) or not (0)
    Knocked :: 0..1,
    % the numbers on the dummies knocked over add up to exactly the target sum
    Values * Knocked #= Target.

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
