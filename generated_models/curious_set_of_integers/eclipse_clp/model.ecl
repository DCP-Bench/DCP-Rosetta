% curious_set_of_integers: an ECLiPSe model from DCP Rosetta.
%
% The integers 1, 3, 8 and 120 form a set in which the product of any two integers is one less than a perfect square.
% Find a fifth number, at least 0, that can be added to the set without destroying this property.
%
% Save this file as model.ecl. Download `curious_set_of_integers.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/curious_set_of_integers.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py curious_set_of_integers.json
%   eclipse -b model.ecl -e "run('curious_set_of_integers_1.dat'), halt"
%
% The data field max_val is the largest value the fifth number may take; the field n (the size of the set once the
% fifth number is added) is not used, since the four members are fixed.

:- lib(ic).

% Number is the fifth number; Roots holds, for each member A of the set, the square root of A*Number+1.
model(Instance, [Number | Roots], [number-Number]) :-
    memberchk(max_val-MaxVal, Instance),
    Number :: 0..MaxVal,
    Limit is 120 * MaxVal + 1,             % R*R = A*Number+1 is at most this, 120 being the largest member

    % for each member A of the set, the product A*Number is one less than a perfect square
    ( foreach(A, [1, 3, 8, 120]), foreach(R, Roots), param(Number, Limit) do
        R :: 0..Limit,
        R * R #= A * Number + 1
    ).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).
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
