% covering_opl: a clingo model from DCP Rosetta.
%
% Select a set of workers to perform all the tasks, while minimizing the cost. Each worker can perform certain tasks
% and has a hiring cost. Ensure that all tasks are performed.
%
% Save this file as model.lp. Download `covering_opl.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/covering_opl.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py covering_opl.json
%   python -m clingo model.lp covering_opl_1.lp
%
% Input: nb_workers(N) holds the number N of workers and num_tasks(T) the number T of tasks; cost(I, C) holds the
% hiring cost C of worker I; qualified(J, K, W) holds when worker W is the K-th worker qualified for task J. Indices
% are 0-based, as in the data, but the worker W is numbered from 1 as in the data, so worker W is worker W-1 here.

worker(0..N-1) :- nb_workers(N).
task(0..T-1) :- num_tasks(T).

% each worker is either hired or not
{ hired(I) } :- worker(I).

% a task is covered when a hired worker is qualified for it
covered(J) :- qualified(J,_,W), hired(W-1).

% every task is performed, so every task is covered
:- task(J), not covered(J).

% the total hiring cost of the workers hired is as small as possible
#minimize { C,I : hired(I), cost(I,C) }.

% total_cost is the total hiring cost of the workers hired
total_cost(S) :- S = #sum { C,I : hired(I), cost(I,C) }.

% workers(I,true) when worker I is hired, workers(I,false) when it is not
workers(I,true) :- hired(I).
workers(I,false) :- worker(I), not hired(I).

#show total_cost/1.
#show workers/2.
