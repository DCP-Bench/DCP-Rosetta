% csplib_010_social_golfers_problem: a clingo model from DCP Rosetta.
%
% A golf club has n_groups * group_size golfers, who play once a week, always in n_groups groups of group_size
% golfers. Find a schedule of play for these golfers over n_weeks weeks such that no golfer plays in the same
% group as any other golfer on more than one occasion.
%
% Save this file as model.lp. Download `csplib_010_social_golfers_problem.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_010_social_golfers_problem.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_010_social_golfers_problem.json
%   python -m clingo model.lp csplib_010_social_golfers_problem_1.lp
%
% Input: n_groups(N), group_size(S), n_weeks(W): the number of groups N, the size S of each group and the number of
% weeks W (indices are 0-based, as in the data).

golfer(0..G-1) :- n_groups(NG), group_size(GS), G = NG * GS.
group(0..N-1) :- n_groups(N).
week(0..W-1) :- n_weeks(W).

% assign(I,J,K): golfer I plays in group K in week J
% each golfer plays in exactly one group each week
1 { assign(I,J,K) : group(K) } 1 :- golfer(I), week(J).

% each group has exactly group_size golfers each week
:- group_size(S), group(K), week(J), #count { I : assign(I,J,K) } != S.

% met(I,I2,J): golfers I and I2 (I < I2) are in the same group in week J
met(I,I2,J) :- assign(I,J,K), assign(I2,J,K), I < I2.

% no golfer plays in the same group as another golfer on more than one occasion
:- golfer(I), golfer(I2), I < I2, #count { J : met(I,I2,J) } > 1.

#show assign/3.
