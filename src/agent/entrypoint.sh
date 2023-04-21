#!/bin/bash

# Run the health_check Flask app in the backgound
python3 health_check.py &

# Run the agent in foreground
python3 agent_learn.py