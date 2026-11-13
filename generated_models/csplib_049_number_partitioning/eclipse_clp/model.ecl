% csplib_049_number_partitioning: an ECLiPSe model from DCP Rosetta.
%
% Find a partition of the numbers 1 to N into two sets A and B such that A and B have the same cardinality, the sum of
% the numbers in A equals the sum of the numbers in B, and the sum of the squares of the numbers in A equals the sum of
% the squares of the numbers in B.
%
% Save this file as model.ecl. Download `csplib_049_number_partitioning.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_049_number_partitioning.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_049_number_partitioning.json
%   eclipse -b model.ecl -e "run('csplib_049_number_partitioning_1.dat'), halt"
%
% The instance field: n (the largest number N, so the numbers are 1 to N).

:- lib(ic).
:- lib(branch_and_bound).

% Outputs the two sets A and B.
model(Instance, Vars, ['A'-As, 'B'-Bs]) :-
    memberchk(n-N, Instance),
    N mod 2 =:= 0,                         % two sets of the same size need an even count
    H is N // 2,                           % the cardinality of each set
    length(As, H),
    length(Bs, H),
    append(As, Bs, Vars),
    Vars :: 1..N,

    % each number from 1 to N is in exactly one of the sets
    alldifferent(Vars),

    % the sums of the numbers in A and in B are equal
    sum(As) #= sum(Bs),

    % the sums of the squares of the numbers in A and in B are equal
    ( foreach(X, As), foreach(S, SqA) do S #= X * X ),
    ( foreach(X, Bs), foreach(S, SqB) do S #= X * X ),
    sum(SqA) #= sum(SqB).

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
