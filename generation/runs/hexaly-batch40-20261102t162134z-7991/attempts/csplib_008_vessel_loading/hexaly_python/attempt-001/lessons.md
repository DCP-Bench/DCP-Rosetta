# csplib_008_vessel_loading attempt-001

Accepted on 2 of 5 instances; on json:1..3 (16 x 16 deck, 10 containers) Hexaly found no
placement in 180 s. After this the reference was read: it lets every container be rotated
(width and length swapped), which this model forbids, so on full-area decks it may have no
solution at all. Next attempt: a Boolean rotation per container. Not attempted in this run
(wall budget spent).
