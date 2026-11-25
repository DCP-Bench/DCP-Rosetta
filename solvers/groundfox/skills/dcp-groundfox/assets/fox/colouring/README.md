# Graph colouring

Writes `colouring.fox` (theory plus a structure built from Python data), grounds it with
`groundfox` and solves the CNF with Glucose 4.2 from python-sat. Run it in an empty folder
with `groundfox` on `PATH`: `python colouring.py`. It prints one proper 3-colouring, for
example `['colour(0,blue)', 'colour(1,red)', 'colour(2,green)', 'colour(3,red)']`.
