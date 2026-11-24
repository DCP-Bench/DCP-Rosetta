% eighteen_hole_golf: a clingo model from DCP Rosetta.
%
% Generate an 18-hole golf course where each hole has a length of 3, 4, or 5, and the total length of the course is 72.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/eighteen_hole_golf.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

hole(0..17).

% each hole has a length of 3, 4 or 5
1 { holes(H, L) : L = 3..5 } 1 :- hole(H).

% the total length of the course is 72
:- #sum { L, H : holes(H, L) } != 72.

#show holes/2.
