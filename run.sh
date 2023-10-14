#!/bin/bash

# Change to the zephyr-chat directory
cd zephyr-chat

# Execute the streamlit command
streamlit run app.py &

# Change back to the previous directory
cd ..

# Change to the zephyr-api directory
cd zephyr-api

# Execute the uvicorn command
uvicorn api:app --reload

# Change back to the previous directory
cd ..
