% media_selection: a MiniZinc model from DCP Rosetta.
%
% The main media selection problem is a problem of allocating advertising budgets between possible
% advertising outlets. Given a set of media options, it aims to determine which media should be selected
% so that all audiences are reached with minimum campaign cost. It does not matter if an audience is
% covered more than once, as long as it is covered at least once. Moreover, the company does not wish to
% spend more money on the campaign than necessary.
%
% Save this file as model.mzn. Download `media_selection.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/media_selection.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py media_selection.json
%   minizinc model.mzn media_selection_1.json

array[int] of int: target_audiences;           % the audiences to reach (only their number is used)
array[int] of int: advertising_media;          % the media options (only their number is used)
array[int,int] of int: incidence_matrix;       % incidence_matrix[t,m] = 1 if medium m reaches audience t
array[int] of int: media_costs;                % media_costs[m]: the cost of medium m

set of int: Audiences = index_set(target_audiences);
set of int: Media = index_set(advertising_media);

array[Media] of var bool: is_selected;         % is_selected[m]: medium m is selected
var int: objective = sum(m in Media)(media_costs[m] * bool2int(is_selected[m]));

% every audience is reached by at least one selected medium
constraint forall(t in Audiences)(sum(m in Media)(incidence_matrix[t,m] * bool2int(is_selected[m])) >= 1);

solve minimize objective;

output ["{\"is_selected\": ", showJSON(is_selected), ", \"min_total_cost\": ", show(objective), "}"];
