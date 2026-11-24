% bin_packing: a clingo model from DCP Rosetta.
%
% Given several items of specific weights and a number of bins of a fixed capacity, assign each item to a bin so that the total weight of the items in each bin does not exceed the capacity.
%
% Save this file as model.lp. Download `bin_packing.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/bin_packing.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py bin_packing.json
%   python -m clingo model.lp bin_packing_1.lp

% Input: capacity(C) and num_bins(B): the capacity C of each bin and the number B of bins;
% weights(I, W): the weight W of item I (indices are 0-based).

item(I) :- weights(I, _).
bin(0..B-1) :- num_bins(B).

% each item is assigned to exactly one bin
1 { bins(I, B) : bin(B) } 1 :- item(I).

% the total weight of the items in each bin does not exceed the capacity
:- capacity(C), bin(B), #sum { W, I : bins(I, B), weights(I, W) } > C.

#show bins/2.
