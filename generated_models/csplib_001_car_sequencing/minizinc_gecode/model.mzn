% csplib_001_car_sequencing: a MiniZinc model from DCP Rosetta.
%
% A number of cars are to be produced; they are not identical, because different options are available
% as variants on the basic model. The assembly line has different stations which install the various
% options. These stations have been designed to handle at most a certain percentage of the cars passing
% along the assembly line. Furthermore, the cars requiring a certain option must not be bunched together,
% otherwise the station will not be able to cope. Consequently, the cars must be arranged in a sequence
% so that the capacity of each station is never exceeded. For example, if a particular station can only
% cope with at most half of the cars passing along the line, the sequence must be built so that at most
% 1 car in any 2 requires that option.
%
% Save this file as model.mzn. Download `csplib_001_car_sequencing.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_001_car_sequencing.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_001_car_sequencing.json
%   minizinc model.mzn csplib_001_car_sequencing_1.json

include "globals.mzn";

array[int] of int: demand;                % demand[t]: the number of cars of car type t to be produced
array[int, int] of int: requires;         % requires[t, o]: 1 if a car of type t requires option o, 0 otherwise
array[int] of int: at_most;               % at_most[o]: a station handles at most this many cars with option o ...
array[int] of int: per_slots;             % ... in any run of this many consecutive cars

set of int: Types = index_set(demand);    % one index per car type
set of int: Options = index_set(at_most); % one index per option
int: n_cars = sum(demand);                % the number of cars
int: n_opts = card(Options);              % the number of options
set of int: Slots = 1..n_cars;            % positions on the assembly line

% option_demand[o]: the number of cars that require option o
array[Options] of int: option_demand = [sum(t in Types)(demand[t] * requires[t, o]) | o in Options];

% load[o]: the share of the capacity of the station of option o that the cars need, scaled by 1000
array[Options] of int: load = [(1000 * option_demand[o] * per_slots[o]) div (at_most[o] * n_cars) | o in Options];
% perm[c]: the option of column c below, the options ordered from the most loaded station to the least
array[Options] of int: perm = arg_sort([-load[o] | o in Options]);

% sequence[s]: the car type at position s of the assembly line
array[Slots] of var Types: sequence;

% skip[s, c] = 1 if the car at position s does not require the option of column c, 0 if it does
array[Slots, Options] of var 0..1: skip;

% the number of cars of each car type is the number demanded
constraint global_cardinality(sequence, [t | t in Types], demand);

% the options of the car at each position are those of its car type, read from the table
array[Types, 1..n_opts + 1] of int: type_rows =
    array2d(Types, 1..n_opts + 1,
            [ if c = 1 then t else 1 - requires[t, perm[c - 1]] endif | t in Types, c in 1..n_opts + 1 ]);
constraint forall(s in Slots)(table([sequence[s]] ++ [skip[s, c] | c in Options], type_rows));

% in every run of per_slots[o] consecutive cars at most at_most[o] of them require option o, so at least
% per_slots[o] - at_most[o] of them do not
constraint forall(c in Options, s in 1..n_cars - per_slots[perm[c]] + 1)(
    sum(k in s..s + per_slots[perm[c]] - 1)(skip[k, c]) >= per_slots[perm[c]] - at_most[perm[c]]);

% room(o, k): the most cars requiring option o that fit in k consecutive cars, a whole run of
% per_slots[o] cars holding at_most[o] of them
function int: room(int: o, int: k) =
    at_most[o] * (k div per_slots[o]) + min(at_most[o], k mod per_slots[o]);

% implied: among the first t cars there are at most room(o, t) cars requiring option o, and at least
% option_demand[o] - room(o, n_cars - t) of them, since the other cars hold at most room(o, n_cars - t)
constraint forall(c in Options, t in 0..n_cars)(
    sum(k in 1..t)(skip[k, c]) <= t - option_demand[perm[c]] + room(perm[c], n_cars - t) /\
    sum(k in 1..t)(skip[k, c]) >= t - room(perm[c], t));

solve satisfy;

% the car types are numbered from 1 here and printed from 0, as the problem asks
output ["{\"sequence\": ", showJSON([fix(sequence[s]) - 1 | s in Slots]), "}"];
