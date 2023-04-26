#!/bin/bash
# while true; do echo "Container is running..."; sleep 60; done
# Run health_check.py in the background
python3 /app/health_check.py &

# Run agent_learn.py and redirect its output to a log file
python3 /app/agent_learn.py > /app/agent_learn.log 2>&1