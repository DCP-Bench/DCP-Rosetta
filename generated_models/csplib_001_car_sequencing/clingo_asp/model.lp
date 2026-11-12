% csplib_001_car_sequencing: a clingo model from DCP Rosetta.
%
% A number of cars are to be produced; they are not identical, because different options are available as variants
% on the basic model. The assembly line has different stations which install the various options (air-conditioning,
% sunroof, etc.). These stations have been designed to handle at most a certain percentage of the cars passing along
% the assembly line. Furthermore, the cars requiring a certain option must not be bunched together, otherwise the
% station will not be able to cope. Consequently, the cars must be arranged in a sequence so that the capacity of
% each station is never exceeded. For example, if a particular station can only cope with at most half of the cars
% passing along the line, the sequence must be built so that at most 1 car in any 2 requires that option.
%
% Save this file as model.lp. Download `csplib_001_car_sequencing.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_001_car_sequencing.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_001_car_sequencing.json
%   python -m clingo model.lp csplib_001_car_sequencing_1.lp
%
% Input: demand(T, N) holds the number N of cars of type T; requires(T, O, V) holds V = 1 when cars of type T
% require option O, and 0 otherwise; at_most(O, M) holds the number M of cars that station O can cope with, among
% every per_slots(O, S) consecutive cars (indices are 0-based, as in the data).

% the number of cars is the sum of the demand of the car types
total(N) :- N = #sum { D,T : demand(T,D) }.
pos(P) :- total(N), P = 0..N-1.

% each position of the sequence holds exactly one car, of some type
1 { car(P,T) : demand(T,_) } 1 :- pos(P).

% the number of cars of each type is its demand
:- demand(T,D), #count { P : car(P,T) } != D.

% needs(P, O): the car at position P requires option O
needs(P,O) :- car(P,T), requires(T,O,1).

% for each option, the station can cope with at most M cars in any S consecutive positions
:- at_most(O,M), per_slots(O,S), total(N), I = 0..N-S,
   #count { P : needs(P,O), P >= I, P < I+S } > M.

% sequence(P, T): the car at position P is of type T
sequence(P,T) :- car(P,T).

#show sequence/2.
