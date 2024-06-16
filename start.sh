#!/bin/bash

# Start the RQ worker in the background
python -m rq worker --url redis://redis:6379/0 &

# Start the Flask app
python run.py
