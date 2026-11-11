% session5_climbing_stairs: a MiniZinc model from DCP Rosetta.
%
% We want to climb a stair of n steps with a number of steps at a time, within a given range [m1, m2]. For
% example a stair of 4 steps with m1 = 1 and m2 = 2 can be climbed with a sequence of four one-step moves or
% with two two-step moves. Find a way to climb a stair of n steps, i.e. you can take only m1 to m2 steps at a
% time.
%
% Save this file as model.mzn. Download `session5_climbing_stairs.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_climbing_stairs.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py session5_climbing_stairs.json
%   minizinc model.mzn session5_climbing_stairs_1.json

int: n;                                    % the number of steps of the stair
int: m1;                                   % the fewest steps taken at one move
int: m2;                                   % the most steps taken at one move

set of int: Moves = 1..n;                  % one index per move; a move of 0 steps is taken after the top

% steps[k]: the number of steps taken at move k
array[Moves] of var 0..m2: steps;

% the moves together climb exactly the n steps of the stair
constraint sum(k in Moves)(steps[k]) = n;

% each move takes between m1 and m2 steps, or no steps at all once the top has been reached
constraint forall(k in Moves)(steps[k] >= m1 \/ steps[k] = 0);

% once a move takes no steps, every later move takes no steps either
constraint forall(k in 2..n)(steps[k - 1] = 0 -> steps[k] = 0);

solve satisfy;
output ["{\"steps\": ", showJSON(steps), "}"];
