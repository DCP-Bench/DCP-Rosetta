% session3_farmer_and_cows: an ECLiPSe model from DCP Rosetta.
%
% A farmer has cows numbered from 1 up to the number of cows, and each cow gives a quantity of milk equal to its
% number. He has several sons, and each son is to get a given number of cows, so that the total milk of the cows
% of each son is the same. Find how the cows can be distributed to the sons.
%
% Save this file as model.ecl. Download `session3_farmer_and_cows.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_farmer_and_cows.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py session3_farmer_and_cows.json
%   eclipse -b model.ecl -e "run('session3_farmer_and_cows_1.dat'), halt"

% num_cows: the number of cows.
% num_sons: the number of sons.
% cows_per_son: the number of cows given to each son, indexed from 0 as in the JSON.

:- lib(ic).
:- lib(lists).
:- lib(listut).

% Son: the son (counted from 0) that each cow goes to, one entry per cow, starting with cow 1.
model(Instance, Son, [cow_assignments-Son]) :-
    memberchk(num_cows-NC, Instance),
    memberchk(num_sons-NS, Instance),
    memberchk(cows_per_son-Counts, Instance),
    length(Son, NC),
    MaxSon is NS - 1,
    Son :: 0..MaxSon,
    numlist(1, NC, Cows),                 % cow i gives i units of milk
    % the milk of all the cows is shared out equally between the sons
    Total is NC * (NC + 1) // 2,
    0 =:= Total mod NS,
    Share is Total // NS,
    % each son gets the number of cows given for him, and his cows give the common share of milk
    ( for(S, 0, MaxSon), param(Son, Counts, Cows, Share, NC) do
        nth0(S, Counts, Count),
        length(Mine, NC),
        ( foreach(Sc, Son), foreach(F, Mine), param(S) do F #= (Sc #= S) ),
        sum(Mine) #= Count,
        Cows * Mine #= Share
    ).

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
