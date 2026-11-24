% csplib_005_autocorrelation: an ECLiPSe model from DCP Rosetta.
%
% Binary sequence with minimum autocorrelation: construct a binary sequence of length n whose
% bits are +1 or -1 and that minimizes the autocorrelations between its bits. With periodic
% (cyclic) boundary conditions, the k-th autocorrelation is C_k = sum over i from 0 to n-1 of
% S_i * S_((i+k) mod n). The aim is to minimize the sum of their squares, E = sum over k from 1
% to n-1 of C_k^2.
%
% Save this file as model.ecl. Download `csplib_005_autocorrelation.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_005_autocorrelation.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_005_autocorrelation.json
%   eclipse -b model.ecl -e "run('csplib_005_autocorrelation_1.dat'), halt"

% Field read from the data: n (the length of the sequence).

:- lib(ic).
:- lib(listut).

model(Instance, Vars, ['sequence'-Seq], min(Energy)) :-
    memberchk(n-N, Instance),
    length(Seq, N),
    % each bit of the sequence is +1 or -1
    Seq :: -1..1,
    ( foreach(Bit, Seq) do Bit #\= 0 ),
    % C_k is the k-th periodic autocorrelation, and its square is added to the energy
    ( for(K, 1, N - 1), foreach(Square, Squares), param(Seq, N) do
        ( for(I, 1, N), foreach(Product, Products), param(Seq, N, K) do
            nth1(I, Seq, Bi),
            J is (I - 1 + K) mod N + 1,
            nth1(J, Seq, Bj),
            Product #= Bi * Bj
        ),
        sum(Products) #= Ck,
        Square #= Ck * Ck
    ),
    % the energy: the sum of the squares of the autocorrelations, to be minimized
    Energy #= sum(Squares),
    Vars = Seq.

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
