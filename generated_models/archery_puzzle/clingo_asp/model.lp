% archery_puzzle: a clingo model from DCP Rosetta.
%
% How close can the young archer come to scoring a total of a target score using as many arrows as she pleases? The targets are given as a list of integers, and each may be hit any number of times. Her score is the sum of the values of all her hits, and the aim is to minimize the absolute difference between that score and the target score.
%
% Save this file as model.lp. Download `archery_puzzle.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/archery_puzzle.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py archery_puzzle.json
%   python -m clingo model.lp archery_puzzle_1.lp

% Input: targets(I, V): hitting target I scores V points; target_score(T): the target score T
% (indices are 0-based, as in the data).

target(I) :- targets(I, _).
max_value(M) :- M = #max { V : targets(_, V) }.

% A score more than the largest value above the target can be improved by removing one arrow,
% so (the values being positive) no best score exceeds the target plus the largest value. The hits are kept within that
% limit, and every hit count H satisfies H * V <= limit.
limit(T+M) :- target_score(T), max_value(M).

% hits(I, H): the archer hits target I H times, and each target gets exactly one count
1 { hits(I, H) : H = 0..L } 1 :- target(I), limit(L).

% the total score of all the hits stays within the limit
:- limit(L), #sum { H * V, I : hits(I, H), targets(I, V) } > L.

% score(S): the total score of the hits
score(S) :- S = #sum { H * V, I : hits(I, H), targets(I, V) }.

% minimize the absolute difference between the score and the target score
#minimize { |T - S| : score(S), target_score(T) }.

#show hits/2.
