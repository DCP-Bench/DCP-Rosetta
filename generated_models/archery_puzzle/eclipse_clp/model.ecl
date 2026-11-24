% archery_puzzle: an ECLiPSe model from DCP Rosetta.
%
% How close can the young archer come to a target score, using as many arrows as she pleases? Each target has a
% value, and she may hit each target any number of times. Her score is the sum of the values of all her hits. The aim
% is to minimise the absolute difference between her score and the target score.
%
% Save this file as model.ecl. Download `archery_puzzle.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/archery_puzzle.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py archery_puzzle.json
%   eclipse -b model.ecl -e "run('archery_puzzle_1.dat'), halt"

% Instance fields: targets (the value of each target, a list indexed from 0), target_score (the score to come close
% to).
:- lib(ic).

model(Instance, Hits, [hits-Hits], min(Gap)) :-
    memberchk(targets-Targets, Instance),
    memberchk(target_score-TargetScore, Instance),
    length(Targets, N),
    length(Hits, N),
    % the number of hits on each target is a whole number, at least 0; a hit scores at least 1, so no target needs
    % more hits than the target score, which keeps the search finite
    Hits :: 0..TargetScore,
    % her score is the sum of the values of all her hits
    Score #= Targets * Hits,
    % the gap between her score and the target score, to be minimised
    Gap #= abs(Score - TargetScore).

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
