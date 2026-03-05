#!/bin/bash

# ANSI color codes - Dark Pink
PINK='\033[38;5;198m'
LIGHT_PINK='\033[38;5;205m'
DIM_PINK='\033[38;5;132m'
RESET='\033[0m'
BOLD='\033[1m'

echo ""
echo -e "${PINK}${BOLD}  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ${RESET}"
echo -e "${PINK}${BOLD}                                              ${RESET}"
echo -e "${PINK}${BOLD}         ELS JUDGE v1.0                       ${RESET}"
echo -e "${PINK}${BOLD}         Development by codedbyelif           ${RESET}"
echo -e "${PINK}${BOLD}                                              ${RESET}"
echo -e "${PINK}${BOLD}  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ${RESET}"
echo ""
echo -e "${LIGHT_PINK}  Starting TUI...${RESET}"
echo ""

python3 cli.py
