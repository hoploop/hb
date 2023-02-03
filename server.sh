#!/bin/bash
export PYTHONPATH=src:$PYTHONPATH
uvicorn hb.api.server:app --host localhost --port 8000 --reload --ssl-keyfile conf/certs/server.key --ssl-certfile conf/certs/server.crt
