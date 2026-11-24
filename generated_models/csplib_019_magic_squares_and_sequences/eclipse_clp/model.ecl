% csplib_019_magic_squares_and_sequences: an ECLiPSe model from DCP Rosetta.
%
% A magic sequence of length n is a sequence of integers x_0, ..., x_{n-1} between 0 and n-1, such that for all i in 0
% to n-1, the number i occurs exactly x_i times in the sequence. For example, 6, 2, 1, 0, 0, 0, 1, 0, 0, 0 is a magic
% sequence, since 0 occurs 6 times in it and 1 occurs twice.
%
% Save this file as model.ecl. Download `csplib_019_magic_squares_and_sequences.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_019_magic_squares_and_sequences.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_019_magic_squares_and_sequences.json
%   eclipse -b model.ecl -e "run('csplib_019_magic_squares_and_sequences_1.dat'), halt"

% Instance field: n, the length of the sequence. Output x: the magic sequence, x[I] for I from 0.

:- lib(ic).
:- lib(ic_global).
:- lib(listut).

model(Instance, Xs, [x-Xs]) :-
    memberchk(n-N, Instance),
    length(Xs, N),
    Max is N - 1,
    % each x_i is between 0 and n-1
    Xs :: 0..Max,
    % for all i in 0 to n-1, the number i occurs exactly x_i times in the sequence
    ( for(I, 0, Max), param(Xs) do
        count_occurrences(I, Xs)
    ).

% the number I occurs exactly x_I times in the sequence
count_occurrences(I, Xs) :-
    nth0(I, Xs, Xi),
    occurrences(I, Xs, Xi).

search_goal(Xs) :-
    search(Xs, 0, first_fail, indomain_min, complete, []).

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
