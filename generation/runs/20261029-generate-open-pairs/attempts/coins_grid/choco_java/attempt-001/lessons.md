Blind model (brief, contracts, dcp-choco skill). Boolean grid with row/column sums and a per-row
lower bound on the squared-distance cost. Search variants tried with a local container run before
the attempt: LCG + diagonal-first input order took 80 s on the example and timed out on json:4
(n=12, c=5); LCG with Choco's default search proved every optimum within 15 s. A position-per-coin
variant with gcc was not needed.
