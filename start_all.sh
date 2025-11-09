#!/bin/bash

echo "==============================================="
echo "SHL Assessment Recommendation System"
echo "Starting API Server and Web UI..."
echo "==============================================="

# Start API in background
echo "Starting API server on port 8000..."
cd src && python api.py &
API_PID=$!

# Wait for API to start
sleep 5

# Start Streamlit UI
echo "Starting Streamlit UI on port 8501..."
streamlit run src/app.py &
UI_PID=$!

echo ""
echo "==============================================="
echo "Services started!"
echo "API: http://localhost:8000"
echo "UI:  http://localhost:8501"
echo "API Docs: http://localhost:8000/docs"
echo "==============================================="
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for both processes
wait $API_PID $UI_PID
