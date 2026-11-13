% candies: an ECLiPSe model from DCP Rosetta.
%
% Alice gives candies to the children of her class, who sit in a line, each with a rating score. Every child gets at
% least 1 candy. Of two children who sit next to each other, the one with the higher rating must get more candies.
% Alice wants to minimize the total number of candies.
%
% Save this file as model.ecl. Download `candies.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/candies.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py candies.json
%   eclipse -b model.ecl -e "run('candies_1.dat'), halt"
%
% Data fields: ratings is the rating score of each child, in line order (a list indexed from 0 as in the JSON).
:- lib(ic).
:- lib(branch_and_bound).

% Outputs: x (the candies of each child) and z (the total number of candies).
model(Instance, Vars, [x-Xs, z-Z], min(Z)) :-
    memberchk(ratings-Ratings, Instance),
    length(Ratings, N),
    length(Xs, N),
    % each child gets at least 1 candy (and never more than N, the length of the line)
    Xs :: 1..N,
    % of two neighbours, the one with the higher rating gets more candies
    neighbours(Ratings, Xs),
    % the total number of candies is the sum over all children
    Z #= sum(Xs),
    append(Xs, [Z], Vars).

% neighbours(Ratings, Xs): every pair of adjacent children obeys the rating rule
neighbours([R1, R2 | Rs], [X1, X2 | Xs]) :-
    (   R1 > R2 -> X1 #> X2
    ;   R1 < R2 -> X1 #< X2
    ;   true
    ),
    neighbours([R2 | Rs], [X2 | Xs]).
neighbours([_], [_]).

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
