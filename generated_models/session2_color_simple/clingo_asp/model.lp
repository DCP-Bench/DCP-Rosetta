% session2_color_simple: a clingo model from DCP Rosetta.
%
% We want to assign a different colour to the following countries: Belgium, Denmark, France, Germany, Netherlands and Luxembourg. Two neighbouring countries cannot have the same colour. You can use integers starting from 1 to represent the colours. Find a colouring that minimizes the number of colours used.
%
% Save this file as model.lp. Download `session2_color_simple.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_color_simple.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py session2_color_simple.json
%   python -m clingo model.lp session2_color_simple_1.lp

% Input: graph(E,P,X): edge E joins the countries graph(E,0,_) and graph(E,1,_), where X is the
% 1-based number of the country (indices are 0-based).

% the countries are numbered 1..N, where N is the largest country number in the edges
endpoint(X) :- graph(_,_,X).
countries(N) :- N = #max { X : endpoint(X) }.
country(1..N) :- countries(N).

% colours are the integers 1..N
colour(1..N) :- countries(N).

% each country has exactly one colour
1 { colourof(I,C) : colour(C) } 1 :- country(I).

% two neighbouring countries have different colours
:- graph(E,0,A), graph(E,1,B), colourof(A,C), colourof(B,C).

% minimize the number of colours used: the highest colour number used, which is that number
% when the colours are numbered from 1 (the optimum uses colours 1..k only)
highest(M) :- M = #max { C : colourof(_,C) }.
#minimize { M : highest(M) }.

% the colour of country I is the I-th entry of the list, counted from 0
colors(I-1,C) :- colourof(I,C).

#show colors/2.
