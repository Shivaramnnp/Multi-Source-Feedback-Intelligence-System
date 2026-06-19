import sys
import json
import logging

# Suppress debug logs
logging.basicConfig(level=logging.WARNING)

from fastapi.testclient import TestClient
from app.main import app

def run():
    print("Initializing TestClient...")
    client = TestClient(app)
    print("Calling /api/v1/intelligence/benchmark...")
    response = client.post("/api/v1/intelligence/benchmark", json={})
    print("Response:")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    run()
