FROM python:3.10.6-slim

COPY src src
COPY requirements.txt requirements.txt
COPY models models
COPY setup.py setup.py

RUN pip install -e .

# Run container locally
# CMD uvicorn api_file:app --reload --host 0.0.0.0

# Run container deployed -> GCP endpoint
# CMD uvicorn src.api_file:app --reload --host 0.0.0.0 --port $PORT

# Run container deployed -> GCP app
CMD streamlit run src/app.py --server.port $PORT --server.address 0.0.0.0
