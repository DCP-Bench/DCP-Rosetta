% jobshop: a clingo model from DCP Rosetta.
%
% One common scheduling problem is the job shop, in which multiple jobs are processed on several machines.
% Each job consists of a sequence of tasks, which must be performed in a given order, and each task must be
% processed on a specific machine. The problem is to schedule the tasks on the machines so as to minimize the
% length of the schedule, the time it takes for all the jobs to be completed. No task for a job can be started
% until the previous task for that job is completed, a machine can only work on one task at a time, and a task,
% once started, must run to completion.
%
% Save this file as model.lp. Download `jobshop.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/jobshop.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py jobshop.json
%   python -m clingo model.lp jobshop_1.lp
%
% Input: jobs_data(J, K, 0, M) and jobs_data(J, K, 1, D): the K-th task of job J (indices are 0-based, as in
% the data) runs on machine M and takes D time units.

task(t(J,K)) :- jobs_data(J,K,0,_).
machine_of(t(J,K),M) :- jobs_data(J,K,0,M).
dur(t(J,K),D) :- jobs_data(J,K,1,D).

% the schedule is no longer than the sum of all the durations
horizon(H) :- H = #sum { D,T : dur(T,D) }.

% start(T, S): the task T starts at time S, each task starts at exactly one time
1 { start(T,S) : S = 0..H } 1 :- task(T), horizon(H).

% no task starts before the previous task of its job has finished
:- start(t(J,K),S), start(t(J,K+1),S2), dur(t(J,K),D), S2 < S + D.

% a machine works on one task at a time: of two tasks on the same machine, one is processed before the other
same_machine(A,B) :- machine_of(A,M), machine_of(B,M), A < B.
1 { before(A,B); before(B,A) } 1 :- same_machine(A,B).

% if A is processed before B, then B does not start before A has finished
:- before(A,B), start(A,SA), start(B,SB), dur(A,DA), SB < SA + DA.

% the makespan is the time at which the last task finishes
makespan(E) :- E = #max { S + D,T : start(T,S), dur(T,D) }.

% minimize the makespan
#minimize { E : makespan(E) }.

% the schedule itself is not part of the answer, so each makespan is reported once
#project makespan/1.
#show makespan/1.
