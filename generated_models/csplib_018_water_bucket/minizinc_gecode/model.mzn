% csplib_018_water_bucket: a MiniZinc model from DCP Rosetta.
%
% You are given an 8 pint bucket of water, and two empty buckets which can contain 5 and 3 pints respectively.
% You are required to divide the water into two by pouring water between buckets (that is, to end up with
% 4 pints in the 8 pint bucket, and 4 pints in the 5 pint bucket).
%
% A transfer pours water from one bucket into another until the first is empty or the second is full. This task is to
% find the minimum number of transfers of water between buckets to reach the goal.
%
% Save this file as model.mzn. Download `csplib_018_water_bucket.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_018_water_bucket.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_018_water_bucket.json
%   minizinc model.mzn csplib_018_water_bucket_1.json

set of int: Buckets = 1..3;                   % the three buckets
array[Buckets] of int: capacities;            % capacities[b]: the most water bucket b can hold
array[Buckets] of int: initial_state;         % the water in each bucket at the start
array[Buckets] of int: goal_state;            % the water in each bucket at the goal
int: MAX_STEPS;                               % the length of the state sequence
int: PADDING_VALUE;                           % marks the steps after the goal has been reached

set of int: Steps = 1..MAX_STEPS;             % the states in the sequence, the first is the start
set of int: Transfers = 1..MAX_STEPS - 1;     % the transfers between consecutive states

% the six ways to pour from one bucket into another: pour_from[p] into pour_to[p]
set of int: Pours = 1..6;
array[Pours] of Buckets: pour_from = [1, 1, 2, 2, 3, 3];
array[Pours] of Buckets: pour_to = [2, 3, 1, 3, 1, 2];

% sequence[t,b]: the water in bucket b in state t, or the padding value
array[Steps, Buckets] of var PADDING_VALUE..max(capacities): sequence;
% active[t]: state t is a real state rather than padding
array[Steps] of var bool: active;
% pour[t,p]: transfer t is the pouring p
array[Transfers, Pours] of var bool: pour;

var int: cost = sum(t in Steps)(bool2int(active[t])) - 1;   % the number of transfers
var int: objective = cost;

% the sequence starts with the initial state
constraint active[1] /\ forall(b in Buckets)(sequence[1, b] = initial_state[b]);

% a real state holds water within the capacity of each bucket, padding marks the other steps
constraint forall(t in Steps, b in Buckets)(active[t] -> sequence[t, b] in 0..capacities[b]);
constraint forall(t in Steps, b in Buckets)(sequence[t, b] = PADDING_VALUE <-> not active[t]);

% the real states come first, the padding after them
constraint forall(t in Transfers)(active[t + 1] -> active[t]);

% each transfer is exactly one pouring, and there is no transfer after the padding starts
constraint forall(t in Transfers)(sum(p in Pours)(bool2int(pour[t, p])) = bool2int(active[t + 1]));

% a pouring moves water from its source bucket until the source is empty or the target bucket is full
constraint forall(t in Transfers, p in Pours)(
    pour[t, p] -> forall(b in Buckets)(
        sequence[t + 1, b] = sequence[t, b]
            - min(sequence[t, pour_from[p]], capacities[pour_to[p]] - sequence[t, pour_to[p]]) * bool2int(b = pour_from[p])
            + min(sequence[t, pour_from[p]], capacities[pour_to[p]] - sequence[t, pour_to[p]]) * bool2int(b = pour_to[p])));

% the last real state is the goal state
constraint forall(t in Transfers)(
    active[t] /\ not active[t + 1] -> forall(b in Buckets)(sequence[t, b] = goal_state[b]));
constraint active[MAX_STEPS] -> forall(b in Buckets)(sequence[MAX_STEPS, b] = goal_state[b]);

solve minimize objective;

output ["{\"cost\": ", show(cost), ", \"sequence\": ", showJSON(sequence), "}"];
