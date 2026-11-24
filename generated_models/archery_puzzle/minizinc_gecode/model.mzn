% archery_puzzle: a MiniZinc model from DCP Rosetta.
%
% How close can the young archer come to scoring a total of a target score using as many arrows as she
% pleases? The targets are given as a list of integers, and each may be hit any number of times. Her score
% is the sum of the values of all her hits, and the aim is to minimize the absolute difference between that
% score and the target score.
%
% Save this file as model.mzn. Download `archery_puzzle.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/archery_puzzle.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py archery_puzzle.json
%   minizinc model.mzn archery_puzzle_1.json

array[int] of int: targets;                    % targets[i]: the value of one hit on target i
int: target_score;                             % the score the archer tries to reach

set of int: Targets = index_set(targets);

% hits[i]: the number of arrows that land on target i. The statement gives no upper bound on it: the
% values may be zero or negative, so no bound on a count can be derived from target_score in general.
% The count is only required to be a whole number that is not negative.
array[Targets] of var int: hits;

% the number of hits on each target is not negative
constraint forall(i in Targets)(hits[i] >= 0);

% the score is the sum of the values of all hits
var int: score = sum(i in Targets)(targets[i] * hits[i]);

% the objective is the distance between the score and the target score
var int: objective = abs(target_score - score);

solve minimize objective;

output ["{\"hits\": ", showJSON(hits), "}"];
