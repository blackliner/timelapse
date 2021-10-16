#!/usr/bin/env python3

import os
import re
import subprocess
from tqdm import tqdm
from pathlib import Path
from datetime import datetime


SCRIPT_FILE = Path(__file__).resolve()
SCRIPT_DIR = SCRIPT_FILE.parent
BASE_DIR = SCRIPT_DIR / "camera"
CALLER_DIR = Path(os.getcwd())


def test_to_date():
    path = BASE_DIR / "reolink01_01_20210609124059.jpg"
    dt = to_date(path)
    assert dt.year == 2021
    assert dt.month == 6
    assert dt.day == 9
    assert dt.hour == 12
    assert dt.minute == 40
    assert dt.second == 59


def to_date(filename: Path) -> datetime:
    match = re.search(r"reolink01_01_([0-9]{4})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})", filename.name)
    year = int(match.group(1))
    month = int(match.group(2))
    day = int(match.group(3))
    hour = int(match.group(4))
    minute = int(match.group(5))
    second = int(match.group(6))
    return datetime(year, month, day, hour, minute, second)


def test_in_range():
    path = BASE_DIR / "reolink01_01_20210609124059.jpg"
    assert in_range(path, [{"start": datetime(2020, 1, 1), "end": datetime(2022, 1, 1)}])
    assert not in_range(path, [{"start": datetime(2022, 1, 1), "end": datetime(2023, 1, 1)}])


def in_range(file: Path, time_ranges):
    for time_range in time_ranges:
        file_date = to_date(file)
        if time_range["start"] < file_date < time_range["end"]:
            return True
    return False


def find_files(time_ranges):
    jpegs = list(BASE_DIR.glob("**/*.jpg"))
    filtered_jpegs = []
    for jpeg in tqdm(jpegs):
        if in_range(jpeg, time_ranges):
            filtered_jpegs.append(jpeg)

    return filtered_jpegs


def create_video(input_files, out_filename):
    input_manifest = SCRIPT_DIR / "manifest.txt"
    with open(input_manifest, "w") as file:
        for path in input_files:
            file.write(f"file {path}\n")

    command = f"ffmpeg -f concat -safe 0 -i {input_manifest} {out_filename}".split()

    subprocess.run(command)


time_ranges = []
time_ranges.append(
    {
        "start": datetime(2021, 7, 29, 7, 0),
        "end": datetime(2021, 7, 29, 17, 0),
    }
)
time_ranges.append(
    {
        "start": datetime(2021, 8, 2),
        "end": datetime(2021, 8, 4),
    }
)

found_files = find_files(time_ranges)

reduced_files = found_files[::5]
reduced_files.sort()

create_video(reduced_files, SCRIPT_DIR / "baustelle_abriss.mp4")

print("hello")
