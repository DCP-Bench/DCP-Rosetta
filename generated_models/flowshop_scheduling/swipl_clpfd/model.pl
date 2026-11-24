% flowshop_scheduling: a SWI-Prolog model from DCP Rosetta.
%
% Jobs must be processed on machines in series, all jobs having the same processing order through machines 1 to M:
% the first job of the sequence goes to machine 1 while the others wait; when machine 1 has finished it, the job goes
% on to machine 2, and the next job starts on machine 1; and so on. Each machine works on one job at a time, and job
% j takes a fixed processing time on machine m. Find the sequence of jobs that minimises the makespan, the time at
% which all jobs have been processed. Give the optimal makespan as an integer.
%
% Save this file as model.pl. Download `flowshop_scheduling.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/flowshop_scheduling.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('flowshop_scheduling.json')" -t halt model.pl
%
% Data fields: process_time (one list per job, indexed from 0, giving the processing time of that job on each
% machine, indexed from 0). The model reads only process_time.
:- use_module(library(clpfd)).

model(Instance, [Starts, Before], [makespan-Makespan], min(Makespan)) :-
    Times = Instance.process_time,           % Times[J][M]: time job J takes on machine M
    length(Times, N),
    Times = [FirstJob|_],
    length(FirstJob, M),
    maplist(sum_list, Times, JobTotals),
    sum_list(JobTotals, Horizon),
    length(Starts, N),
    maplist(starts_for(M, Horizon), Starts),  % Starts[J][M]: start time of job J on machine M
    % a job starts on a machine only after it has finished on the previous machine
    maplist(job_chain, Starts, Times),
    % the same order of jobs on every machine: for each pair of jobs, one comes first on all machines
    order_pairs(Starts, Times, Before),
    % the makespan is at least the finish time of every job on the last machine
    maplist(job_finish(Makespan), Starts, Times),
    Makespan in 0..Horizon.

starts_for(M, Horizon, Row) :-
    length(Row, M),
    Row ins 0..Horizon.

job_chain([S|Ss], [P|Ps]) :-
    chain_rest(S, P, Ss, Ps).

chain_rest(_, _, [], []).
chain_rest(S, P, [S2|Ss], [P2|Ps]) :-
    S + P #=< S2,
    chain_rest(S2, P2, Ss, Ps).

order_pairs([], [], []).
order_pairs([S|Ss], [P|Ps], Bs) :-
    maplist(order_with(S, P), Ss, Ps, Bs1),
    order_pairs(Ss, Ps, Bs2),
    append(Bs1, Bs2, Bs).

% B is 1 when job S goes before job K on every machine, 0 when K goes before S on every machine
order_with(S, P, K, Q, B) :-
    B in 0..1,
    both_orders(S, P, K, Q, B).

both_orders([], [], [], [], _).
both_orders([S|Ss], [P|Ps], [K|Ks], [Q|Qs], B) :-
    B #==> (S + P #=< K),
    (#\ B) #==> (K + Q #=< S),
    both_orders(Ss, Ps, Ks, Qs, B).

job_finish(Makespan, Ss, Ps) :-
    last(Ss, SLast),
    last(Ps, PLast),
    SLast + PLast #=< Makespan.

:- use_module(library(http/json)).

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
solve_file(File) :- solve_file(File, 1).
solve_file(File, N) :-
    setup_call_cleanup(open(File, read, Stream),
                       json_read_dict(Stream, Data, [value_string_as(atom)]),
                       close(Stream)),
    (   is_list(Data) -> nth1(N, Data, Instance) ; Instance = Data ),
    solve_model(Instance).

solve_model(Instance) :-
    (   current_predicate(model/4)
    ->  model(Instance, Vars, Outputs, Objective)
    ;   model(Instance, Vars, Outputs), Objective = none
    ),
    (   current_predicate(labeling_options/1) -> labeling_options(Options) ; Options = [ff] ),
    term_variables(Vars-Outputs, All),
    (   Objective == none
    ->  labeling(Options, All)
    ;   once(labeling([Objective|Options], All))
    ),
    forall(member(Name-Value, Outputs), format("~w = ~w~n", [Name, Value])).
