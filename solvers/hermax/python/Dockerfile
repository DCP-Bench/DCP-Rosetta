FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7
# hermax brings its own cardinality and pseudo-Boolean encoders, and pulls
# python-sat in for the SAT and RC2 backends its Model layer solves with
# (stratified RC2 by default since 1.2.9).
COPY solvers/hermax/python/requirements.txt /opt/requirements.txt
RUN pip install --no-cache-dir --require-hashes --only-binary=:all: -r /opt/requirements.txt
COPY runner/runtime.py /opt/runner/runtime.py
COPY solvers/hermax/python/run.py /opt/runner/run.py
ENTRYPOINT ["python", "/opt/runner/run.py"]
