#!/bin/bash
cp -n .env.example .env
echo "Starting She Check API..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
