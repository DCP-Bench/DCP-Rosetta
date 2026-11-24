% csplib_002_template_design: a clingo model from DCP Rosetta.
%
% This problem arises from a colour printing firm which produces a variety of products from thin board, including
% cartons for human and animal food and magazine inserts. Packaging for such variations usually has the same overall
% design, in particular the same size and shape, but differs in a small proportion of the text displayed and/or in
% colour. A typical order is for a variety of quantities of several design variations. Because each variation is
% identical in dimension, we know in advance exactly how many items can be printed on each mother sheet of board.
% Each mother sheet is printed from a template, consisting of a thin aluminium sheet on which the design for several
% of the variations is etched. The problem is to decide, for a given number of templates with a given number of slots
% each, which variations, and how many copies of each, to include on each template, and how many sheets to take from
% each template. Every slot of a template is filled. Each template yields between 1 sheet and as many sheets as the
% largest demand. The sheets printed must meet at least the demand of every variation, and the objective is to
% minimize the total number of printed sheets.
%
% Save this file as model.lp. Download `csplib_002_template_design.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_002_template_design.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_002_template_design.json
%   python -m clingo model.lp csplib_002_template_design_1.lp
%
% Input: n_templates(T) holds the number T of templates; n_slots(S) the number S of slots of each template;
% n_var(V) the number V of variations; demand(I, D) the demand D of variation I (indices are 0-based, as in the data).

template(0..T-1) :- n_templates(T).
variation(0..V-1) :- n_var(V).
largest_demand(M) :- M = #max { D : demand(_,D) }.

% layout(T, I, K): template T has K slots for variation I, one number K for each variation
1 { layout(T,I,K) : K = 0..S } 1 :- template(T), variation(I), n_slots(S).

% every slot of a template is filled
:- template(T), n_slots(S), #sum { K,I : layout(T,I,K) } != S.

% printed_ge(T, P): template T is printed P times or more, for P = 2 up to the largest demand. The sheets of
% each template are counted in this order encoding, so that the number of sheets is a count the solver can reason about.
{ printed_ge(T,P) : P = 2..M } :- template(T), largest_demand(M).

% if a template is printed P+1 times or more, it is printed P times or more
:- printed_ge(T,P+1), not printed_ge(T,P), P >= 2.

% production(T, P): template T is printed exactly P times, between 1 and the largest demand
production(T,1) :- template(T), not printed_ge(T,2).
production(T,P) :- printed_ge(T,P), not printed_ge(T,P+1).

% the templates are interchangeable, so they are numbered in order of the sheets printed, most sheets first
:- template(T), printed_ge(T+1,P), not printed_ge(T,P).

% items_ge(T, I, X): the sheets of template T carry X items of variation I or more, for X up to the demand of I.
% On the first sheet the K copies of I on the template are carried; each further item needs the sheets that the
% copies of I on the template are printed on: X items need ceiling(X / K) sheets when the template carries K copies.
items_ge(T,I,X) :- layout(T,I,K), demand(I,D), X = 1..K, X <= D.
items_ge(T,I,X) :- layout(T,I,K), K >= 1, demand(I,D), X = K+1..D, printed_ge(T,(X+K-1)/K).

% the demand of every variation is met: the items of the variation over all templates reach its demand
:- demand(I,D), #count { T,X : items_ge(T,I,X) } < D.

% the total number of printed sheets is as small as possible: the first sheet of each template counts once, and
% each further sheet is counted by one printed_ge atom
#minimize { 1,T,first : template(T) ; 1,T,P : printed_ge(T,P) }.

% layout(T,I,K) and production(T,P) are shown: the number of each variation on each template, and the number of
% sheets printed from each template
#show layout/3.
#show production/2.
