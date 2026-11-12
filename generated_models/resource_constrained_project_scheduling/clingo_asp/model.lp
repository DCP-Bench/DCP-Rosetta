% resource_constrained_project_scheduling: a clingo model from DCP Rosetta.
%
% The resource-constrained project scheduling problem involves scheduling a set of jobs, each with a specific duration and resource requirement, such that the total project duration (makespan) is minimized. Each job may have precedence constraints, meaning certain jobs must be completed before others can start. Additionally, there are multiple types of resources, each with a limited capacity that must not be exceeded at any time. Given the durations of the jobs, their resource requirements, the capacities of the resources, and the precedence constraints between the jobs, determine the start times of the jobs that minimize the makespan while satisfying all constraints.
%
% Save this file as model.lp. Download `resource_constrained_project_scheduling.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/resource_constrained_project_scheduling.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py resource_constrained_project_scheduling.json
%   python -m clingo model.lp resource_constrained_project_scheduling_1.lp
%
% Input: durations_data(J, D) the duration D of job J; resource_needs_data(J, R, Q) the amount Q of resource R that
% job J uses while it runs; resource_capacities_data(R, C) the capacity C of resource R; successors_link_data(K, 0, P)
% and successors_link_data(K, 1, S): job S may start only after job P has finished (indices are 0-based, as in the data).

job(J) :- durations_data(J,_).
resource(R) :- resource_capacities_data(R,_).
precedes(P,S) :- successors_link_data(K,0,P), successors_link_data(K,1,S).

% the time horizon: the total duration of all jobs, so that no job needs to start later than this
horizon(H) :- H = #sum { D,J : durations_data(J,D) }.
time(0..H) :- horizon(H).

% start_time(J,T): job J starts at time T
1 { start_time(J,T) : time(T) } 1 :- job(J).

% each job starts after all its predecessors have finished
:- precedes(P,S), start_time(P,T1), durations_data(P,D), start_time(S,T2), T2 < T1 + D.

% running(J,T): job J is running at time T, that is, it started at time S with S <= T < S + D
running(J,T) :- start_time(J,S), durations_data(J,D), T = S..S+D-1.

% at every time, the jobs running use no more of a resource than its capacity
:- resource(R), resource_capacities_data(R,C), time(T),
   #sum { Q,J : running(J,T), resource_needs_data(J,R,Q) } > C.

% finish(J,F): job J finishes at time F; makespan(M): M is the latest finish time of all jobs
finish(J,S+D) :- start_time(J,S), durations_data(J,D).
makespan(M) :- M = #max { F : finish(_,F) }.

% the makespan is as small as possible
#minimize { M : makespan(M) }.

#show start_time/2.
