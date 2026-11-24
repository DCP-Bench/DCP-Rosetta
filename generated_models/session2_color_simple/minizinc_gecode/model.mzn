% session2_color_simple: a MiniZinc model from DCP Rosetta.
%
% We want to assign a different colour to the following countries: Belgium, Denmark, France, Germany, Netherlands
% and Luxembourg. Two neighbouring countries cannot have the same colour. You can use integers starting from 1 to
% represent the colours. Find a colouring that minimizes the number of colours used.
%
% Save this file as model.mzn. Download `session2_color_simple.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_color_simple.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py session2_color_simple.json
%   minizinc model.mzn session2_color_simple_1.json

array[int, int] of int: graph;                 % graph[e,1], graph[e,2]: the two neighbouring countries of edge e

int: num_countries = 6;                        % Belgium, Denmark, France, Germany, Netherlands, Luxembourg (numbered in this order)
set of int: Countries = 1..num_countries;
set of int: Colours = 1..num_countries;        % at most one colour per country is ever needed
set of int: Edges = index_set_1of2(graph);     % one index per pair of neighbouring countries

array[Countries] of var Colours: colors;       % colors[c]: the colour of country c
var int: objective = max(colors);              % the number of colours used, when the colours are 1..k

% two neighbouring countries have different colours
constraint forall(e in Edges)(colors[graph[e, 1]] != colors[graph[e, 2]]);

solve minimize objective;
output ["{\"colors\": ", showJSON(colors), "}"];
