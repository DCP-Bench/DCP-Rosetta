% csplib_002_template_design: a MiniZinc model from DCP Rosetta.
%
% This problem arises from a colour printing firm which produces a variety of products from thin board.
% Each mother sheet is printed from a template, consisting of a thin aluminium sheet on which the design
% for several of the variations is etched. The problem is to decide, for a given number of templates
% with a given number of slots each, which variations, and how many copies of each, to include on each
% template, and how many sheets to make from each template. Every slot of a template is filled. Each
% template yields between 1 sheet and as many sheets as the largest demand. The sheets produced must meet
% at least the demand of every variation, and the objective is to minimize the total number of
% sheets produced.
%
% Save this file as model.mzn. Download `csplib_002_template_design.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_002_template_design.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_002_template_design.json
%   minizinc model.mzn csplib_002_template_design_1.json

int: n_templates;                       % the number of templates
int: n_slots;                           % the number of slots on each template
int: n_var;                             % the number of design variations
array[int] of int: demand;              % demand[v]: the number of sheets of variation v ordered

set of int: Templates = 1..n_templates; % one index per template
set of int: Vars = 1..n_var;            % one index per variation
int: max_sheets = max(demand);          % no template yields more sheets than the largest demand

% layout[t, v]: the number of slots of template t given to variation v
array[Templates, Vars] of var 0..n_slots: layout;
% production[t]: the number of sheets made from template t
array[Templates] of var 1..max_sheets: production;

% every slot of each template is filled
constraint forall(t in Templates)(sum(v in Vars)(layout[t, v]) = n_slots);

% the sheets made from the templates meet the demand of every variation
constraint forall(v in Vars)(sum(t in Templates)(layout[t, v] * production[t]) >= demand[v]);

% implied: each sheet carries n_slots items, so the sheets made must cover the total demand
constraint n_slots * sum(t in Templates)(production[t]) >= sum(v in Vars)(demand[v]);

var int: objective = sum(t in Templates)(production[t]);

solve minimize objective;

output ["{\"production\": ", showJSON(production), ", \"layout\": ", showJSON(layout), "}"];
