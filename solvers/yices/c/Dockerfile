FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7 AS yices-build
# Yices 2.7.0 with MCSAT, built from source at pinned commits (libpoly, CUDD, Yices).
RUN apt-get update && apt-get install -y --no-install-recommends gcc=4:12.2.0-3 g++=4:12.2.0-3 make=4.3-4.1 cmake=3.25.1-1 autoconf=2.71-3 automake=1:1.16.5-1.3 libtool=2.4.7-7~deb12u1 gperf=3.1-1 libgmp-dev=2:6.2.1+dfsg1-1.1 git ca-certificates && rm -rf /var/lib/apt/lists/*
RUN git clone --branch v0.2.1 https://github.com/SRI-CSL/libpoly.git /src/libpoly \
 && test "$(git -C /src/libpoly rev-parse HEAD)" = "3d5e6fbd98639cb0941b029e23ca17c0e3c4a80a" \
 && cmake -S /src/libpoly -B /build/libpoly -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/opt/yices -DLIBPOLY_BUILD_PYTHON_API=OFF -DLIBPOLY_BUILD_STATIC=OFF \
 && cmake --build /build/libpoly -j2 && cmake --install /build/libpoly
RUN git clone --branch cudd-3.0.0 https://github.com/ivmai/cudd.git /src/cudd \
 && test "$(git -C /src/cudd rev-parse HEAD)" = "f54f533303640afd5dbe47a05ebeabb3066f2a25" \
 && cd /src/cudd && autoreconf -fi && ./configure --enable-shared --prefix=/opt/yices && make -j2 && make install
RUN git clone --branch yices-2.7.0 https://github.com/SRI-CSL/yices2.git /src/yices2 \
 && test "$(git -C /src/yices2 rev-parse HEAD)" = "85cf17e44eac76b5d14b297c09fc9bfecf47ef65" \
 && cd /src/yices2 && autoconf && CPPFLAGS=-I/opt/yices/include LDFLAGS=-L/opt/yices/lib ./configure --enable-mcsat --prefix=/opt/yices \
 && make -j2 && make install

FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7
RUN apt-get update && apt-get install -y --no-install-recommends gcc=4:12.2.0-3 libc6-dev libgmp10=2:6.2.1+dfsg1-1.1 libgmp-dev=2:6.2.1+dfsg1-1.1 libcjson-dev=1.7.15-1+deb12u4 && rm -rf /var/lib/apt/lists/*
COPY --from=yices-build /opt/yices /opt/yices
RUN echo /opt/yices/lib > /etc/ld.so.conf.d/yices.conf && ldconfig
ENV C_INCLUDE_PATH=/opt/yices/include LIBRARY_PATH=/opt/yices/lib
COPY solvers/yices/c/c /opt/c
RUN gcc -std=gnu11 -O2 -Wall -I/opt/c -c /opt/c/driver.c -o /opt/c/driver.o
COPY --chmod=0755 runner/runtime.py solvers/yices/c/run.py /opt/runner/
ENTRYPOINT ["python", "/opt/runner/run.py"]
