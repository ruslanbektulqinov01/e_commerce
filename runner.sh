#!/bin/bash

echo "Formatting code..."

black .

echo "Black formatting done successfully!"

sleep 1

pip freeze > requirements.txt

echo "Requirements updated successfully!"

sleep 1

uvicorn app.main:app --reload --port 8000
