#!/bin/bash

# ANSI color codes - Dark Pink
PINK='\033[38;5;198m'
LIGHT_PINK='\033[38;5;205m'
DIM_PINK='\033[38;5;132m'
RESET='\033[0m'
BOLD='\033[1m'

echo ""
echo -e "${PINK}${BOLD}  ♥ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ♥${RESET}"
echo -e "${PINK}${BOLD}  ♥                                             ♥${RESET}"
echo -e "${PINK}${BOLD}  ♥      LLM Consensus Engine v1.0              ♥${RESET}"
echo -e "${PINK}${BOLD}  ♥      Development by codedbyelif             ♥${RESET}"
echo -e "${PINK}${BOLD}  ♥                                             ♥${RESET}"
echo -e "${PINK}${BOLD}  ♥ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ♥${RESET}"
echo ""
echo -e "${LIGHT_PINK}  Starting services...${RESET}"
echo ""

# Start the FastAPI backend in the background
echo -e "${DIM_PINK}  [1/2]${RESET} ${LIGHT_PINK}FastAPI backend${RESET} → http://localhost:8000"
uvicorn main:app --host 0.0.0.0 --port 8000 &

sleep 2

# Start the Streamlit dashboard in the foreground
echo -e "${DIM_PINK}  [2/2]${RESET} ${LIGHT_PINK}Streamlit dashboard${RESET} → http://localhost:8501"
echo ""
echo -e "${PINK}${BOLD}  ♥ Ready! Open http://localhost:8501 in your browser${RESET}"
echo ""
streamlit run dashboard/app.py --server.port=8501 --server.address=0.0.0.0
