% flowshop_scheduling: an ECLiPSe model from DCP Rosetta.
%
% A set of jobs need to be processed on a set of machines in series. All jobs have the same processing order through all
% the machines from machine 1 to machine M. Each machine can work in parallel. The first job of the sequence goes to the
% first machine to be processed; meanwhile, other jobs wait; when the first machine has processed the first job, the
% first job goes to the second machine and the second job of the sequence starts to be processed by the first machine;
% and so on. The time required to process job j on machine m is ProcesTime_{j, m}. Find a sequence of jobs that
% minimizes the makespan, the time when all jobs have been processed.
%
% Save this file as model.ecl. Download `flowshop_scheduling.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/flowshop_scheduling.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py flowshop_scheduling.json
%   eclipse -b model.ecl -e "run('flowshop_scheduling_1.dat'), halt"
%
% The data fields: process_time[j][m] is the time job j (numbered from 0 in the list, job j+1 in the model) needs on
% machine m (numbered from 0). The other fields are not needed.

:- lib(ic).
:- lib(listut).

% Seq[K] is the job (1-based) in position K of the sequence, and Mk is the makespan.
model(Instance, Seq, [makespan-Mk], min(Mk)) :-
    memberchk(process_time-PT, Instance),
    length(PT, N),
    PT = [Row1 | _],
    length(Row1, M),

    % Ub, the sum of all processing times, bounds every completion time
    ( foreach(Row, PT), fromto(0, A, B, Ub) do
          ( foreach(X, Row), fromto(A, A1, A2, B) do A2 is A1 + X )
    ),

    % every job takes exactly one position
    length(Seq, N),
    Seq :: 1..N,
    alldifferent(Seq),

    % Cols[Mc] lists the processing time of every job (by job number) on machine Mc
    columns(1, M, PT, Cols),

    % the completion times, machine by machine, of the job in each position of the sequence
    length(Zeros, M),
    ( foreach(Z, Zeros) do Z = 0 ),
    schedule(Seq, Cols, M, Ub, Zeros, Final),
    nth1(M, Final, Mk),
    Mk :: 0..Ub.

search_goal(Seq) :-
    search(Seq, 0, first_fail, indomain_min, complete, []).

% columns(+Mc, +Mmax, +PT, -Cols): Cols lists, for each machine, the processing time of every job
columns(Mc, Mmax, _, []) :-
    Mc > Mmax, !.
columns(Mc, Mmax, PT, [Col|Cols]) :-
    ( foreach(R, PT), foreach(V, Col), param(Mc) do nth1(Mc, R, V) ),
    Mc1 is Mc + 1,
    columns(Mc1, Mmax, PT, Cols).

% schedule(+Seq, +Cols, +M, +Ub, +Prev, -Final): the positions of the sequence in order; Prev holds the completion times
% of the previous position (zeros before the first one)
schedule([], _, _, _, Prev, Prev).
schedule([S|Ss], Cols, M, Ub, Prev, Final) :-
    row(1, M, S, Cols, Ub, Prev, 0, Row),
    schedule(Ss, Cols, M, Ub, Row, Final).

% row(+Mc, +M, +S, +Cols, +Ub, +Prev, +Left, -Row): the completion times of job S on machines Mc to M. The job starts on
% machine Mc when the machine is free (the previous job left it, Up) and the job has left machine Mc-1 (Left).
row(Mc, M, _, _, _, _, _, []) :-
    Mc > M, !.
row(Mc, M, S, Cols, Ub, Prev, Left, [C|Cs]) :-
    nth1(Mc, Cols, Col),
    element(S, Col, P),
    nth1(Mc, Prev, Up),
    C :: 0..Ub,
    C #= max(Up, Left) + P,
    Mc1 is Mc + 1,
    row(Mc1, M, S, Cols, Ub, Prev, C, Cs).

% Reads the data file, builds the model, solves it and prints each output.
run(File) :-
    open(File, read, Stream), read(Stream, Instance), close(Stream),
    solve_model(Instance).

:- lib(branch_and_bound).

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
