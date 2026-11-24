% de_bruijn_sequence: an ECLiPSe model from DCP Rosetta.
%
% A de Bruijn sequence of order n on a size-k alphabet is a cyclic sequence in which every possible length-n string
% on the alphabet occurs exactly once as a substring. It has length k^n.
%
% Save this file as model.ecl. Download `de_bruijn_sequence.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/de_bruijn_sequence.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py de_bruijn_sequence.json
%   eclipse -b model.ecl -e "run('de_bruijn_sequence_1.dat'), halt"
%
% The data fields: base is the size k of the alphabet (symbols 0 to k-1) and n the order; the sequence is cyclic.

:- lib(ic).
:- lib(listut).

% Xs[I] is the symbol at position I (0-based) of the cyclic sequence.
model(Instance, Vars, [de_bruijn-Xs]) :-
    memberchk(base-B, Instance),
    memberchk(n-N, Instance),
    Len is B ^ N,
    Max is Len - 1,
    length(Xs, Len),
    Xs :: 0..B-1,

    % Codes[I] is the base-B value of the length-n window that starts at position I (read cyclically)
    length(Codes, Len),
    Codes :: 0..Max,
    ( for(I, 0, Max), foreach(C, Codes), param(Xs, Len, B, N) do
        window_code(Xs, Len, B, N, I, C)
    ),

    % every length-n string occurs exactly once: all the window codes are different
    alldifferent(Codes),
    flatten([Xs, Codes], Vars).

% C is the base-B value of the length-N window of the cyclic sequence Xs that starts at position I
window_code(Xs, Len, B, N, I, C) :-
    ( for(J, 0, N-1), foreach(T, Terms), param(Xs, Len, B, N, I) do
        K is (I + J) mod Len,
        P is B ^ (N - 1 - J),
        nth0(K, Xs, X),
        T #= X * P
    ),
    C #= sum(Terms).

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
