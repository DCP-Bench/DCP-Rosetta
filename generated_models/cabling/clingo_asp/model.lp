% cabling: a clingo model from DCP Rosetta.
%
% A rack cabinet holds 1U devices, such as servers and routers, which must be connected by cables. Some
% devices must be connected by several cables. Each device takes one position in the rack, and neighbouring
% positions are one unit apart. A cable between two devices is as long as the distance between their
% positions, so connecting them by k cables costs k times that distance. Place the devices in such an order
% that the sum of all cable lengths is as short as possible.
%
% Save this file as model.lp. Download `cabling.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/cabling.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py cabling.json
%   python -m clingo model.lp cabling_1.lp

% Input: n(N) gives the number N of devices, which is also the number of rack positions; devices(I, D)
% holds the name D of device I; cable_struct(K, 0, A), cable_struct(K, 1, B) and cable_struct(K, 2, C)
% say that cable group K joins devices A and B with C cables (indices are 0-based, as in the data).

device(I) :- devices(I, _).
slot(0..N-1) :- n(N).

% the gaps between neighbouring positions: gap G lies between positions G and G+1
gap(0..N-2) :- n(N).

% each device takes exactly one rack position, and each position holds exactly one device
1 { pos(I, P) : slot(P) } 1 :- device(I).
1 { pos(I, P) : device(I) } 1 :- slot(P).

% the devices joined by a cable group, by their indices
cable(K, I1, I2, C) :- cable_struct(K, 0, A), cable_struct(K, 1, B), cable_struct(K, 2, C),
                       devices(I1, A), devices(I2, B).

% a device lies below gap G when its position is G or less
low(I, G) :- pos(I, P), gap(G), P <= G.

% a cable group crosses gap G when exactly one of its two devices lies below the gap
crosses(K, G) :- cable(K, I1, I2, _), gap(G), low(I1, G), not low(I2, G).
crosses(K, G) :- cable(K, I1, I2, _), gap(G), low(I2, G), not low(I1, G).

% a cable spans as many gaps as its length, so the total cable length is the number of cables
% crossing each gap, summed over the gaps and the cable groups
final_sum(S) :- S = #sum { C,K,G : cable(K, _, _, C), crosses(K, G) }.

% the total cable length is as short as possible
#minimize { S : final_sum(S) }.

#show final_sum/1.
