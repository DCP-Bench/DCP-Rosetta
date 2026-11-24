% devils_word: an ECLiPSe model from DCP Rosetta.
%
% Given an array of integers, insert '+' or '-' before each integer so that summing them up gives a given total. For
% example, with the array [1, 2, 3] and the total 4, the signs -1, 2, 3 are a solution.
%
% Save this file as model.ecl. Download `devils_word.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/devils_word.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py devils_word.json
%   eclipse -b model.ecl -e "run('devils_word_1.dat'), halt"
%
% The data fields: arr is the array of integers and total the target sum; arr is indexed from 0 as in the JSON.

:- lib(ic).
:- lib(listut).

% Signs[I] is 1 when the I-th integer gets a '+' and 0 when it gets a '-'.
model(Instance, Signs, [result-Results]) :-
    memberchk(arr-Arr, Instance),
    memberchk(total-Total, Instance),
    length(Arr, N),
    length(Signs, N),
    Signs :: 0..1,
    length(Results, N),

    % each signed integer is the integer itself or its negation
    ( foreach(A, Arr), foreach(S, Signs), foreach(R, Results) do
        R #= A * (2 * S - 1)
    ),

    % the signed integers sum to the total
    sum(Results) #= Total.

search_goal(Signs) :-
    search(Signs, 0, first_fail, indomain_min, complete, []).
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
