% flowshop_scheduling: a clingo model from DCP Rosetta.
%
% A set of jobs need to be processed on a set of machines in series. All jobs have the same processing
% order through all the machines from machine 1 to machine M. Each machine can work in parallel. The
% workflow is the following: the first job of the sequence goes to the first machine to be processed;
% meanwhile, other jobs wait; when the first machine has processed the first job, the first job goes to
% the second machine and the second job of the sequence starts to be processed by the first machine; and
% so on. The problem aims to minimize the total makespan: the time when all jobs have been processed.
%
% Save this file as model.lp. Download `flowshop_scheduling.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/flowshop_scheduling.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py flowshop_scheduling.json
%   python -m clingo model.lp flowshop_scheduling_1.lp
%
% Input: jobs(J, V) holds the job J (indices are 0-based, as in the data); machines(M, V) holds the machine M;
% process_time(J, M, D) holds the time D that job J takes on machine M.

% the jobs and the machines are those that have a value
job(J) :- jobs(J, _).
machine(M) :- machines(M, _).

% the positions of the sequence, counted from 0, are the jobs
slot(K) :- job(K).

% sequence(K, J): job J is the K-th job of the sequence; every position holds exactly one job and every
% job takes exactly one position
1 { sequence(K, J) : job(J) } 1 :- slot(K).
1 { sequence(K, J) : slot(K) } 1 :- job(J).

% duration(K, M, D): the K-th job of the sequence takes D time units on machine M
duration(K, M, D) :- sequence(K, J), process_time(J, M, D).

% ge(K, M, T): the K-th job of the sequence finishes on machine M at time T or later. A job starts at
% time 0 at the earliest. It starts on a machine once it has finished on the previous machine, and once
% the previous job of the sequence has finished on this machine, so each of these finishing times pushes
% its finishing time later by the processing time. A finish at T implies a finish at T - 1 or later.
ge(K, M, D) :- duration(K, M, D), D > 0.
ge(K, M, T + D) :- duration(K, M, D), ge(K, M - 1, T).
ge(K, M, T + D) :- duration(K, M, D), ge(K - 1, M, T).
ge(K, M, T - 1) :- ge(K, M, T), T > 1.

% the makespan is the time at which the last job of the sequence finishes on the last machine
last_slot(K) :- K = #max { I : slot(I) }.
last_machine(M) :- M = #max { I : machine(I) }.
makespan(T) :- last_slot(K), last_machine(M), ge(K, M, T), not ge(K, M, T + 1).

% minimize the makespan
#minimize { T : makespan(T) }.

% only the makespan is reported, so the sequence is projected away
#project makespan/1.
#show makespan/1.
