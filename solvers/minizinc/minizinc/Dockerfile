FROM minizinc/minizinc:2.9.3@sha256:df57458b590f53fbd68114b59563cf9e5a32ca8e8385865dc6a553635a90a7f3 AS minizinc
FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7
COPY --from=minizinc /usr/local /usr/local
COPY solvers/minizinc/minizinc/requirements.txt /opt/requirements.txt
RUN pip install --no-cache-dir --require-hashes --only-binary=:all: -r /opt/requirements.txt
COPY runner/runtime.py /opt/runner/runtime.py
COPY solvers/minizinc/minizinc/run.py /opt/runner/run.py
ENTRYPOINT ["python", "/opt/runner/run.py"]
