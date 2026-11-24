% session3_exodus: an ECLiPSe model from DCP Rosetta.
%
% In preparation for Passover, five children at Hebrew school (Bernice, Carl, Debby, Sammy and Ted) have each
% chosen a different part of the story of the Exodus from Egypt: the burning bush, the captivity, Moses's youth,
% the Passover, or the Ten Commandments. Each child is a different age (three, five, seven, eight or ten), and
% each child's family made its own exodus to America from a different country (Ethiopia, Kazakhstan, Lithuania,
% Morocco or Yemen). Find the age, the family's country and the part of the story of each child. The clues:
% Debby's family is from Lithuania; the child who told the story of the Passover is two years older than
% Bernice; the child whose family is from Yemen is younger than the child from the Ethiopian family; the child
% from the Moroccan family is three years older than Ted; Sammy is three years older than the child who told the
% story of Moses's youth.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_exodus.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

% The model reads no data; its clues are the constraints below. The children are numbered 1 to 5 in the order Bernice, Carl, Debby, Sammy, Ted.
% The ages are numbered 1 to 5 for three, five, seven, eight and ten years; the countries for Ethiopia, Kazakhstan, Lithuania, Morocco and Yemen; the stories for the burning bush, the captivity, Moses's youth, the Passover and the Ten Commandments.
% Each list gives, at each slot, the child (numbered as above) who has that age, country or story, so the four lists link each child to one age, country and story.

:- lib(ic).
:- lib(lists).

model(_Instance, Vars, [ages-Ages, children-[1, 2, 3, 4, 5], countries-Countries, stories-Stories]) :-
    length(Ages, 5),
    length(Countries, 5),
    length(Stories, 5),
    % the age, country and story slot of Bernice, Carl, Debby, Sammy and Ted
    AgeSlots = [AgeB, AgeC, AgeD, AgeS, AgeT],
    CountrySlots = [CtyB, CtyC, CtyD, CtyS, CtyT],
    StorySlots = [StB, StC, StD, StS, StT],
    AgeSlots :: 1..5,
    CountrySlots :: 1..5,
    StorySlots :: 1..5,
    % each child has a different age, country and story
    alldifferent(AgeSlots),
    alldifferent(CountrySlots),
    alldifferent(StorySlots),
    Ages :: 1..5,
    Countries :: 1..5,
    Stories :: 1..5,
    % each list holds each child at the slot of his or her age, country and story
    element(AgeB, Ages, 1), element(AgeC, Ages, 2), element(AgeD, Ages, 3),
    element(AgeS, Ages, 4), element(AgeT, Ages, 5),
    element(CtyB, Countries, 1), element(CtyC, Countries, 2), element(CtyD, Countries, 3),
    element(CtyS, Countries, 4), element(CtyT, Countries, 5),
    element(StB, Stories, 1), element(StC, Stories, 2), element(StD, Stories, 3),
    element(StS, Stories, 4), element(StT, Stories, 5),
    % the age in years of each child: slot 1 is three years, slot 5 is ten years
    Years = [YB, YC, YD, YS, YT],
    AgeYears = [3, 5, 7, 8, 10],
    element(AgeB, AgeYears, YB), element(AgeC, AgeYears, YC),
    element(AgeD, AgeYears, YD), element(AgeS, AgeYears, YS),
    element(AgeT, AgeYears, YT),
    % Debby's family is from Lithuania (country 3)
    CtyD #= 3,
    % the child who told the story of the Passover (story 4) is two years older than Bernice
    years_at(StorySlots, Years, 4, PassoverYears),
    PassoverYears #= YB + 2,
    % the child whose family is from Yemen (country 5) is younger than the child from the Ethiopian family (country 1)
    years_at(CountrySlots, Years, 5, YemenYears),
    years_at(CountrySlots, Years, 1, EthiopiaYears),
    YemenYears #< EthiopiaYears,
    % the child from the Moroccan family (country 4) is three years older than Ted
    years_at(CountrySlots, Years, 4, MoroccoYears),
    MoroccoYears #= YT + 3,
    % Sammy is three years older than the child who told the story of Moses's youth (story 3)
    years_at(StorySlots, Years, 3, MosesYears),
    YS #= MosesYears + 3,
    append([AgeSlots, CountrySlots, StorySlots, Ages, Countries, Stories], Vars).

% Y is the age in years of the child whose slot in Slots is Slot
years_at(Slots, Years, Slot, Y) :-
    ( foreach(S, Slots), foreach(Yc, Years), param(Slot, Y) do
        AtSlot #= (S #= Slot),
        SameYears #= (Y #= Yc),
        AtSlot #=< SameYears
    ).

:- lib(branch_and_bound).

% Solves the model and prints each output.
run :- solve_model([]).

solve_model(Instance) :-
    (   current_module(gfd) -> Lib = gfd ; Lib = ic ),
    (   current_predicate(model/4)
    ->  model(Instance, Vars, Outputs, Objective)
    ;   model(Instance, Vars, Outputs), Objective = none
    ),
    (   Objective = max(Expr)
    ->  call(Lib:(Total #= Expr)), call(Lib:(Cost #= -Total)),
        minimize(run_search(Vars, Outputs), Cost)
    ;   Objective = min(Expr)
    ->  call(Lib:(Cost #= Expr)),
        minimize(run_search(Vars, Outputs), Cost)
    ;   run_search(Vars, Outputs)
    ),
    ( foreach(Name-Value, Outputs) do printf("%w = %w%n", [Name, Value]) ).

run_search(Vars, Outputs) :-
    (   current_predicate(search_goal/1) -> search_goal(Vars) ; labeling(Vars) ),
    term_variables(Outputs, Free),
    labeling(Free).
