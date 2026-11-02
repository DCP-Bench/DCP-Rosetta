# Hexaly needs a licence file whenever an optimizer is created, and the container has
# no network, so the licence enters at build time as the build secret `hexaly_license`:
# evaluation.build passes it when DCP_SECRET_HEXALY_LICENSE names the file. Built
# without it, the image works for everything except solving, which fails with Hexaly's
# "Cannot open file [/opt/hexaly_15_0/license.dat]"; a machine whose layer cache holds
# a build with it reuses that layer. An image built with it holds the licence: keep it
# on the machine that built it, never push, save or cache it remotely.
FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7
COPY solvers/hexaly/python/requirements.txt /opt/requirements.txt
RUN pip install --no-cache-dir --require-hashes --only-binary=:all: -r /opt/requirements.txt
RUN --mount=type=secret,id=hexaly_license,required=false \
    if [ -s /run/secrets/hexaly_license ]; then \
        install -D -m 0444 /run/secrets/hexaly_license /opt/hexaly_15_0/license.dat; \
    fi
COPY runner/runtime.py /opt/runner/runtime.py
COPY solvers/hexaly/python/run.py /opt/runner/run.py
ENTRYPOINT ["python", "/opt/runner/run.py"]
