% csplib_008_vessel_loading: a clingo model from DCP Rosetta.
%
% Supply vessels transport containers from site to site. The deck is a rectangle, and the containers are cuboids
% laid out in a single layer, each parallel to the sides of the deck, with its width and length in that order or
% rotated by 90 degrees. Two containers may touch but must not overlap. Containers of certain classes must be
% separated by minimum distances, either along the deck or across it. Decide whether the given containers can be
% positioned on the given deck without overlapping and without violating any separation constraint, and give
% such a positioning.
%
% Save this file as model.lp. Download `csplib_008_vessel_loading.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_008_vessel_loading.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_008_vessel_loading.json
%   python -m clingo model.lp csplib_008_vessel_loading_1.lp
%
% Input: deck_width(W), deck_length(L): the width and length of the deck; n_containers(N): the number of containers;
% width(I,W), length(I,L), classes(I,C): the width, length and class (from 1) of container I; separation(A,B,S): classes A+1 and B+1 keep distance S (0-based).

cont(0..N-1) :- n_containers(N).
xcoord(0..W) :- deck_width(W).
ycoord(0..L) :- deck_length(L).

% each container is either turned by 90 degrees or not
{ turned(I) } :- cont(I).

% the lower left corner of each container is at a point of the deck
1 { left(I,X) : xcoord(X) } 1 :- cont(I).
1 { bottom(I,Y) : ycoord(Y) } 1 :- cont(I).

% the upper right corner follows from the lower left corner and the width and length in the orientation chosen
right(I,X+W) :- left(I,X), width(I,W), not turned(I).
right(I,X+L) :- left(I,X), length(I,L), turned(I).
top(I,Y+L) :- bottom(I,Y), length(I,L), not turned(I).
top(I,Y+W) :- bottom(I,Y), width(I,W), turned(I).

% every container lies on the deck
:- right(I,X), deck_width(W), X > W.
:- top(I,Y), deck_length(L), Y > L.

% gap(I,J,S): containers I and J (I < J) must keep the distance S, given by the separation of their classes
gap(I,J,S) :- cont(I), cont(J), I < J, classes(I,A), classes(J,B), separation(A-1,B-1,S).

% apart(I,J): one of the two containers lies beside the other, across or along the deck, with the distance S between them
apart(I,J) :- gap(I,J,S), right(I,R), left(J,L), R + S <= L.
apart(I,J) :- gap(I,J,S), right(J,R), left(I,L), R + S <= L.
apart(I,J) :- gap(I,J,S), top(I,T), bottom(J,B), T + S <= B.
apart(I,J) :- gap(I,J,S), top(J,T), bottom(I,B), T + S <= B.

% no two containers overlap, and containers whose classes have a separation keep that distance
:- gap(I,J,_), not apart(I,J).

#show left/2.
#show right/2.
#show top/2.
#show bottom/2.
