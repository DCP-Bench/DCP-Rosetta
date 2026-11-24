% packing_rectangles: a clingo model from DCP Rosetta.
%
% The rectangular packing problem involves placing a set of rectangular items into a larger rectangular area such that no items overlap and all items are within the boundaries of the larger area. The objective is to minimize the total area of the larger rectangle required to pack all the items. Given the widths and heights of the items, determine their positions within the larger rectangle while ensuring no overlap and minimizing the total area.
%
% Save this file as model.lp. Download `packing_rectangles.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/packing_rectangles.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py packing_rectangles.json
%   python -m clingo model.lp packing_rectangles_1.lp
%
% Input: widths(I, W) and heights(I, H) hold the width W and the height H of item I (indices are 0-based).

item(I) :- widths(I,_).
sum_w(S) :- S = #sum { W,I : widths(I,W) }.
sum_h(S) :- S = #sum { H,I : heights(I,H) }.

% pos_x(I,X): item I starts in column X; pos_y(I,Y): item I starts in row Y.
% An item never starts beyond the sum of all widths (heights) minus its own width (height).
1 { pos_x(I,X) : X = 0..S-W } 1 :- widths(I,W), sum_w(S).
1 { pos_y(I,Y) : Y = 0..S-H } 1 :- heights(I,H), sum_h(S).

% total_x and total_y: the width and the height of the rectangle that holds the items
1 { total_x(X) : X = 1..S } 1 :- sum_w(S).
1 { total_y(Y) : Y = 1..S } 1 :- sum_h(S).

% every item lies within the rectangle
:- pos_x(I,X), widths(I,W), total_x(T), X + W > T.
:- pos_y(I,Y), heights(I,H), total_y(T), Y + H > T.

% no two items overlap: for each pair, one item lies entirely left of the other, or entirely below it
% (left(A,B): item A lies entirely left of item B; below(A,B): item A lies entirely below item B)
1 { left(A,B); left(B,A); below(A,B); below(B,A) } :- item(A), item(B), A < B.
:- left(A,B), pos_x(A,XA), widths(A,W), pos_x(B,XB), XA + W > XB.
:- below(A,B), pos_y(A,YA), heights(A,H), pos_y(B,YB), YA + H > YB.

% the area of the rectangle is as small as possible
#minimize { X*Y : total_x(X), total_y(Y) }.

#show pos_x/2.
#show pos_y/2.
#show total_x/1.
#show total_y/1.
