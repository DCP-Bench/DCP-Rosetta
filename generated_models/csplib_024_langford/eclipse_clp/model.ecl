% csplib_024_langford: an ECLiPSe model from DCP Rosetta.
%
% Consider two sets of the numbers from 1 to k. The problem is to arrange the 2k numbers in the two sets into a single
% sequence in which the two 1's appear one number apart, the two 2's appear two numbers apart, ..., and the two k's
% appear k numbers apart.
%
% Save this file as model.ecl. Download `csplib_024_langford.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_024_langford.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_024_langford.json
%   eclipse -b model.ecl -e "run('csplib_024_langford_1.dat'), halt"
%
% The instance field: k (the largest number; the sets hold the numbers 1 to k).

:- lib(ic).
:- lib(branch_and_bound).

% Output sol: the sequence of the 2k numbers, position 1 first.
model(Instance, Cells, [sol-Sol]) :-
    memberchk(k-K, Instance),
    N is 2*K,                              % the number of positions in the sequence
    length(Sol, N),                        % Sol[P] is the number at position P
    Sol :: 1..K,
    % As[I] and Bs[I] are the positions of the two copies of the number I
    length(As, K),
    length(Bs, K),
    As :: 1..N,
    Bs :: 1..N,
    % the two copies of I have exactly I numbers between them (the usual Langford reading of 'I numbers apart'), so the second copy comes I+1 positions after the first
    ( for(I, 1, K), foreach(A, As), foreach(B, Bs), param(Sol) do
        B #= A + I + 1,
        element(A, Sol, I),
        element(B, Sol, I)
    ),
    % the 2k numbers are arranged into one sequence: each position holds exactly one number
    append(As, Bs, Cells),
    alldifferent(Cells).

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
