# Yices 2.7.0 built from source with MCSAT (libpoly, CUDD), then the official
# Python bindings on top. The build stage is identical to solvers/yices/c/Dockerfile
# so Docker shares its layers: keep the two copies in sync.
FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7 AS yices-build
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      gcc=4:12.2.0-3 g++=4:12.2.0-3 make=4.3-4.1 cmake=3.25.1-1 \
      autoconf=2.71-3 automake=1:1.16.5-1.3 libtool=2.4.7-7~deb12u1 \
      gperf=3.1-1 libgmp-dev=2:6.2.1+dfsg1-1.1 git ca-certificates \
 && rm -rf /var/lib/apt/lists/*
RUN git clone --branch v0.2.1 https://github.com/SRI-CSL/libpoly.git /src/libpoly \
 && cd /src/libpoly \
 && test "$(git rev-parse HEAD)" = 3d5e6fbd98639cb0941b029e23ca17c0e3c4a80a \
 && cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/opt/yices \
      -DLIBPOLY_BUILD_PYTHON_API=OFF -DLIBPOLY_BUILD_STATIC=OFF \
 && cmake --build build -j2 && cmake --install build
RUN git clone --branch cudd-3.0.0 https://github.com/ivmai/cudd.git /src/cudd \
 && cd /src/cudd \
 && test "$(git rev-parse HEAD)" = f54f533303640afd5dbe47a05ebeabb3066f2a25 \
 && autoreconf -fi && ./configure --enable-shared --prefix=/opt/yices \
 && make -j2 && make install
RUN git clone --branch yices-2.7.0 https://github.com/SRI-CSL/yices2.git /src/yices2 \
 && cd /src/yices2 \
 && test "$(git rev-parse HEAD)" = 85cf17e44eac76b5d14b297c09fc9bfecf47ef65 \
 && autoconf \
 && CPPFLAGS=-I/opt/yices/include LDFLAGS=-L/opt/yices/lib ./configure --enable-mcsat --prefix=/opt/yices \
 && make -j2 && make install

FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7
RUN apt-get update \
 && apt-get install -y --no-install-recommends libgmp10=2:6.2.1+dfsg1-1.1 \
 && rm -rf /var/lib/apt/lists/*
COPY --from=yices-build /opt/yices /opt/yices
RUN echo /opt/yices/lib > /etc/ld.so.conf.d/yices.conf && ldconfig
# Bindings only (no shared CP requirements: runner/runtime.py imports lazily).
# 1.1.6 wheel sha256 pinned.
RUN echo "yices==1.1.6 --hash=sha256:030321a6a926a7992cb380cd597f2df81f06c56644daad790c7e832d2cd4a780" > /tmp/req.txt \
 && pip install --no-cache-dir --require-hashes -r /tmp/req.txt && rm /tmp/req.txt
RUN python -c "from yices import Yices; print(Yices.version)"
COPY runner/runtime.py /opt/runner/runtime.py
COPY solvers/yices/python/run.py /opt/runner/run.py
ENTRYPOINT ["python", "/opt/runner/run.py"]
