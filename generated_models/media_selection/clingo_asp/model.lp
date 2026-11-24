% media_selection: a clingo model from DCP Rosetta.
%
% The main media selection problem is a problem of allocating advertising budgets between possible advertising outlets. Given a set of media options, it aims to determine which media should be selected so that all audiences are reached with minimum campaign cost. It does not matter if an audience is covered more than once, as long as it is covered at least once. Moreover, the company does not wish to spend more money on the campaign than necessary.
%
% Save this file as model.lp. Download `media_selection.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/media_selection.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py media_selection.json
%   python -m clingo model.lp media_selection_1.lp
%
% Input: target_audiences(T, V) the value V of audience T; advertising_media(M, V) the value V of medium M;
% incidence_matrix(T, M, W) is 1 when medium M reaches audience T, 0 otherwise; media_costs(M, C) the cost C
% of medium M (indices are 0-based, as in the data).

audience(T) :- target_audiences(T,_).
medium(M) :- advertising_media(M,_).

% chosen(M): medium M is selected
{ chosen(M) : medium(M) }.

% every audience is reached by at least one selected medium
:- audience(T), #sum { W,M : chosen(M), incidence_matrix(T,M,W) } < 1.

% the total cost of the selected media
min_total_cost(S) :- S = #sum { C,M : chosen(M), media_costs(M,C) }.

% the total cost of the campaign is as small as possible
#minimize { C,M : chosen(M), media_costs(M,C) }.

% is_selected(M,true/false): whether medium M is selected
is_selected(M,true) :- chosen(M).
is_selected(M,false) :- medium(M), not chosen(M).

#show is_selected/2.
#show min_total_cost/1.
