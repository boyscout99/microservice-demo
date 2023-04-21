#!/bin/bash

# Run the health_check Flask app in the backgound
python3 app/health_check.py &

# Run the agent in foreground
python3 app/agent_learn.py