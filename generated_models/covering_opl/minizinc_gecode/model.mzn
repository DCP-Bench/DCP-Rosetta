% covering_opl: a MiniZinc model from DCP Rosetta.
%
% Select a set of workers to perform all the tasks, while minimizing the cost. Each worker can perform
% certain tasks and has a hiring cost. Ensure that all tasks are performed.
%
% Save this file as model.mzn. Download `covering_opl.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/covering_opl.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py covering_opl.json
%   minizinc model.mzn covering_opl_1.json

int: nb_workers;                                % the number of workers
int: num_tasks;                                 % the number of tasks
array[int] of int: Cost;                        % Cost[w]: the hiring cost of worker w
array[int, int] of int: Qualified;              % Qualified[t, k]: the k-th worker who can perform task t
array[int] of int: Qualified_len;               % Qualified_len[t]: the number of workers who can perform task t

set of int: Workers = 1..nb_workers;             % one index per worker
set of int: Tasks = 1..num_tasks;               % one index per task

% hired[w]: worker w is hired
array[Workers] of var bool: hired;
% total_cost: the total hiring cost of the hired workers
var int: total_cost = sum(w in Workers)(Cost[w] * bool2int(hired[w]));

% every task is performed by a hired worker who can perform it
constraint forall(t in Tasks)(
    sum(k in 1..Qualified_len[t])(bool2int(hired[Qualified[t, k]])) >= 1);

var int: objective = total_cost;

solve minimize objective;

output ["{\"total_cost\": ", showJSON(total_cost), ", \"workers\": ", showJSON(hired), "}"];
