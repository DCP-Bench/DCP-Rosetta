# GroundFOX: proof-logging grounder of finite-domain FO into DIMACS CNF (KU Leuven,
# MPL-2.0). It ships as C++ source only and needs C++23 and CMake >= 3.25, so it is
# built on trixie (gcc 14, cmake 3.31) at a pinned commit; libstdc++ is linked
# statically. ANTLR's runtime and jar are fetched by its CMake. The SAT solver is
# CaDiCaL 3.0.0 from python-sat 1.9.dev25, run in a child process killed at the deadline.
FROM python:3.12.11-slim-trixie@sha256:0b29ab9e420820f53d1cd5ce0157dfe07bea8a7cff5b4754d6d95c07b0e5bc47 AS build
COPY --chmod=0755 solvers/apt-snapshot.sh /usr/local/bin/apt-snapshot
RUN apt-snapshot 20261027T090227Z && apt-get update \
 && apt-get install -y --no-install-recommends g++ cmake make git default-jre-headless ca-certificates
ARG GROUNDFOX_COMMIT=f30fb9ce7341425bfb04a19851f6901cc0dbf88d
RUN git clone https://gitlab.kuleuven.be/krr/software/groundfox-checkfox.git /src \
 && cd /src && git checkout "$GROUNDFOX_COMMIT" \
 && cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF \
      -DCMAKE_EXE_LINKER_FLAGS="-static-libstdc++ -static-libgcc" \
 && cmake --build build --parallel 8 \
 && install -m 0755 build/groundfox/groundfox build/checkfox/checkfox /usr/local/bin/

FROM python:3.12.11-slim-trixie@sha256:0b29ab9e420820f53d1cd5ce0157dfe07bea8a7cff5b4754d6d95c07b0e5bc47
COPY --from=build /usr/local/bin/groundfox /usr/local/bin/checkfox /usr/local/bin/
COPY solvers/groundfox/fox/requirements.txt /opt/requirements.txt
RUN pip install --no-cache-dir --require-hashes --only-binary=:all: -r /opt/requirements.txt
COPY runner/runtime.py /opt/runner/runtime.py
COPY solvers/groundfox/fox/run.py solvers/groundfox/fox/dcp_fox.py /opt/runner/
ENTRYPOINT ["python", "/opt/runner/run.py"]
