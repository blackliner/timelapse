#!/bin/bash
# set -euxo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# YEAR=2021
# MONTH=07
# FILE="/home/fberchtold/camera/myvideo-${MONTH}-${YEAR}.mp4"

# rm -f "$FILE"
# find "/home/fberchtold/camera/camera/${YEAR}/${MONTH}" -name "*.jpg" | sort | awk 'NR==1||NR % 1 == 0' | sed "~s/^/file /" >~/camera/source.txt
# ffmpeg -f concat -safe 0 -i ~/camera/source.txt "$FILE"


conan install ffmpeg/4.4@ -if ${SCRIPT_DIR}/temp -g virtualrunenv -b missing

. ${SCRIPT_DIR}/temp/activate_run.sh

${SCRIPT_DIR}/create.py
