% csplib_084_hadamard_matrix: an ECLiPSe model from DCP Rosetta.
%
% For every odd positive integer l, with m = (l - 1) / 2, find two sequences A = [a_1..a_l] and B = [b_1..b_l] of
% values -1 or +1 such that, for every shift s = 1..m, the periodic autocorrelations of A and of B at s add up to -2,
% where the periodic autocorrelation PAF(X, s) is the sum over i of x_i * x_(i+s), indices taken modulo l. Also the
% entries of A sum to 1 and the entries of B sum to 1.
%
% Save this file as model.ecl. Download `csplib_084_hadamard_matrix.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_084_hadamard_matrix.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_084_hadamard_matrix.json
%   eclipse -b model.ecl -e "run('csplib_084_hadamard_matrix_1.dat'), halt"
%
% The data field l is the length of each sequence (an odd number).

:- lib(ic).
:- lib(listut).

% As and Bs are the two sequences, entries -1 or +1.
model(Instance, Vars, [a-As, b-Bs]) :-
    memberchk(l-L, Instance),
    M is (L - 1) // 2,
    length(As, L),
    length(Bs, L),
    As :: [-1, 1],
    Bs :: [-1, 1],
    flatten([As, Bs], Vars),

    % for each shift S = 1..m, the autocorrelations of A and of B at S add up to -2
    ( for(S, 1, M), param(As, Bs, L) do
        periodic_autocorrelation(As, S, L, PA),
        periodic_autocorrelation(Bs, S, L, PB),
        PA + PB #= -2
    ),

    % the entries of A sum to 1
    sum(As) #= 1,

    % the entries of B sum to 1
    sum(Bs) #= 1.

% PAF(Xs, S): the sum over I = 1..L of X_I * X_((I+S) mod L), with 1-based positions
periodic_autocorrelation(Xs, S, L, PAF) :-
    ( for(I, 1, L), foreach(T, Ts), param(Xs, S, L) do
        J is (I - 1 + S) mod L + 1,
        nth1(I, Xs, XI), nth1(J, Xs, XJ),
        T #= XI * XJ
    ),
    PAF #= sum(Ts).

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
