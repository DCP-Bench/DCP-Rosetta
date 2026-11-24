% csplib_018_water_bucket: a clingo model from DCP Rosetta.
%
% You are given an 8 pint bucket of water, and two empty buckets which can contain 5 and 3 pints respectively. You are required to divide the water into two by pouring water between buckets (that is, to end up with 4 pints in the 8 pint bucket, and 4 pints in the 5 pint bucket). A transfer pours water from one bucket into another until the first is empty or the second is full. This task is to find the minimum number of transfers of water between buckets to reach the goal.
%
% Save this file as model.lp. Download `csplib_018_water_bucket.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_018_water_bucket.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_018_water_bucket.json
%   python -m clingo model.lp csplib_018_water_bucket_1.lp

% Input: capacities(B, C): the capacity C of bucket B; initial_state(B, A) and goal_state(B, A): the
% starting and goal amounts A of bucket B; mAX_STEPS(M): the length M of the sequence of states;
% pADDING_VALUE(P): the value P that pads the sequence after the goal (indices are 0-based).

bucket(B) :- capacities(B, _).
step(0..M-1) :- mAX_STEPS(M).

% the amount a bucket can hold runs from 0 up to its capacity
amount(B, 0..C) :- capacities(B, C).

% state(T,B,A): after T transfers, bucket B holds A pints; the sequence starts from the initial state
state(0, B, A) :- initial_state(B, A).
active(T) :- state(T, _, _).

% the goal is reached in state T when every bucket holds its goal amount
off_goal(T) :- active(T), goal_state(B, A), not state(T, B, A).
at_goal(T) :- active(T), not off_goal(T).

% pour_option(T,I,J,Q): in state T, bucket I can be poured into bucket J, moving Q pints: bucket I holds
% water, bucket J has room, and the amount moved is the smaller of the water in I and the room in J
pour_option(T, I, J, Q) :- active(T), not at_goal(T), step(T+1), state(T, I, X), state(T, J, Y),
                           capacities(J, C), I != J, X > 0, Y < C, Q = #min { X ; C - Y }.

% each state that is not the goal is followed by exactly one transfer
1 { pour(T, I, J, Q) : pour_option(T, I, J, Q) } 1 :- active(T), not at_goal(T).

% after a transfer the source loses Q pints, the target gains Q pints, and the other buckets keep their amounts
state(T+1, I, X-Q) :- pour(T, I, J, Q), state(T, I, X), amount(I, X-Q).
state(T+1, J, Y+Q) :- pour(T, I, J, Q), state(T, J, Y), amount(J, Y+Q).
state(T+1, B, A)   :- pour(T, I, J, Q), state(T, B, A), B != I, B != J.

% the sequence lists the states; after the goal, each remaining step is the padding state
sequence(T, B, A) :- state(T, B, A).
sequence(T, B, P) :- step(T), not active(T), bucket(B), pADDING_VALUE(P).

% the cost is the number of transfers
cost(C) :- C = #count { T : active(T), T > 0 }.

% the minimum number of transfers is sought
#minimize { 1, T, I, J, Q : pour(T, I, J, Q) }.

#show cost/1.
#show sequence/3.
