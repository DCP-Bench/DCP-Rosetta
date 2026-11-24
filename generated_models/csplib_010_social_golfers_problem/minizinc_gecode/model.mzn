% csplib_010_social_golfers_problem: a MiniZinc model from DCP Rosetta.
%
% The coordinator of a local golf club has n_groups * group_size golfers, each of whom plays golf
% once a week, always in n_groups groups of group_size golfers. Make a schedule of play for these
% golfers over n_weeks weeks, such that no golfer plays in the same group as any other golfer on
% more than one occasion.
%
% Save this file as model.mzn. Download `csplib_010_social_golfers_problem.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_010_social_golfers_problem.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_010_social_golfers_problem.json
%   minizinc model.mzn csplib_010_social_golfers_problem_1.json

include "globals.mzn";

int: n_weeks;                                  % the number of weeks
int: n_groups;                                 % the number of groups played each week
int: group_size;                               % the number of golfers in each group
int: n_golfers = n_groups * group_size;        % every golfer plays every week

set of int: Golfers = 1..n_golfers;            % one index per golfer
set of int: Weeks = 1..n_weeks;                % one index per week
set of int: Groups = 0..n_groups - 1;          % the groups, numbered from 0

% assign[g, w]: the group golfer g plays in during week w
array[Golfers, Weeks] of var Groups: assign;

% every week, each group has exactly group_size golfers
constraint forall(w in Weeks)(
    global_cardinality([assign[g, w] | g in Golfers], [gr | gr in Groups], [group_size | gr in Groups]));

% no two golfers are in the same group in more than one week
constraint forall(g1, g2 in Golfers where g1 < g2)(
    sum(w in Weeks)(bool2int(assign[g1, w] = assign[g2, w])) <= 1);

solve satisfy;
output ["{\"assign\": ", showJSON(assign), "}"];
