% twelve_pack: a clingo model from DCP Rosetta.
%
% Given a target number of items, find the combination of packs of different sizes whose total number of items is at
% least the target and as close to it as possible.
%
% Save this file as model.lp. Download `twelve_pack.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/twelve_pack.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py twelve_pack.json
%   python -m clingo model.lp twelve_pack_1.lp
%
% Input: target(T) holds the target number T of items; packs(I, P) holds the number P of items in pack size I
% (0-based, as in the data).

% counts(I, V): V packs of size I are bought. No optimal solution buys more packs of one size than needed to
% reach the target, so V is bounded by T / P + 1.
1 { counts(I, V) : V = 0..T / P + 1 } 1 :- packs(I, P), target(T).

% the total number of items bought is at least the target
:- target(T), #sum { P * V, I : counts(I, V), packs(I, P) } < T.

% the total number of items is as close to the target as possible, that is as small as possible
#minimize { P * V, I : counts(I, V), packs(I, P) }.

#show counts/2.
