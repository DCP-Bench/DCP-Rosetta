#!/bin/sh
# Minion as Savile Row starts it for the optimisation run, unchanged: same binary, same
# arguments. Savile Row deletes Minion's solutions file (-solsout) once it has read the
# last line, so before Minion starts this gives that file a second name in the working
# directory, dcp_incumbents.sols, which run.py follows for the improving solutions.
previous=
for argument in "$@"; do
    if [ "$previous" = "-solsout" ]; then
        ln -f "$argument" dcp_incumbents.sols 2>/dev/null
    fi
    previous=$argument
done
exec /opt/savilerow/bin/minion "$@"
