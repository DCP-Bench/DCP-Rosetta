% contracting_costs: a MiniZinc model from DCP Rosetta.
%
% A contractor planning the construction of a house found that he would have to pay: $1,100 to the
% paper hanger and the painter, $1,700 to the painter and plumber, $1,100 to the plumber and
% electrician, $3,300 to the electrician and carpenter, $5,300 to the carpenter and mason, and $3,200
% to the mason and painter.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/contracting_costs.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

int: largest_payment = 5300;  % the largest sum paid to two men, which bounds each charge

var 0..largest_payment: paper_hanger;   % the charge of the paper hanger
var 0..largest_payment: painter;        % the charge of the painter
var 0..largest_payment: plumber;        % the charge of the plumber
var 0..largest_payment: electrician;    % the charge of the electrician
var 0..largest_payment: carpenter;      % the charge of the carpenter
var 0..largest_payment: mason;          % the charge of the mason

% the contractor pays 1100 to the paper hanger and the painter
constraint paper_hanger + painter = 1100;
% the contractor pays 1700 to the painter and the plumber
constraint painter + plumber = 1700;
% the contractor pays 1100 to the plumber and the electrician
constraint plumber + electrician = 1100;
% the contractor pays 3300 to the electrician and the carpenter
constraint electrician + carpenter = 3300;
% the contractor pays 5300 to the carpenter and the mason
constraint carpenter + mason = 5300;
% the contractor pays 3200 to the mason and the painter
constraint mason + painter = 3200;

solve satisfy;

output ["{\"paper_hanger\": ", showJSON(paper_hanger),
        ", \"painter\": ", showJSON(painter),
        ", \"plumber\": ", showJSON(plumber),
        ", \"electrician\": ", showJSON(electrician),
        ", \"carpenter\": ", showJSON(carpenter),
        ", \"mason\": ", showJSON(mason), "}"];
