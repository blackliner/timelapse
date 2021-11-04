#!/usr/bin/env python3

import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List

import cv2
from tqdm import tqdm

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
    match = re.search(
        r"reolink01_01_([0-9]{4})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})",
        filename.name,
    )
    year = int(match.group(1))
    month = int(match.group(2))
    day = int(match.group(3))
    hour = int(match.group(4))
    minute = int(match.group(5))
    second = int(match.group(6))
    return datetime(year, month, day, hour, minute, second)


def test_in_range():
    path = BASE_DIR / "reolink01_01_20210609124059.jpg"
    assert in_range(
        path, [{"start": datetime(2020, 1, 1), "end": datetime(2022, 1, 1)}]
    )
    assert not in_range(
        path, [{"start": datetime(2022, 1, 1), "end": datetime(2023, 1, 1)}]
    )


def in_range(file: Path, time_ranges):
    for time_range in time_ranges:
        file_date = to_date(file)
        if time_range["start"] < file_date < time_range["end"]:
            return True
    return False


def find_files(time_ranges) -> List[Path]:
    jpegs = list(BASE_DIR.glob("**/*.jpg"))
    filtered_jpegs = []
    print("Filtering images:")
    for jpeg in tqdm(jpegs):
        if in_range(jpeg, time_ranges):
            filtered_jpegs.append(jpeg)

    return filtered_jpegs


FPS = 60
assert FPS != 0
FRAME_DURATION = 1 / FPS
VIDEO_LENGTH = 10  # in seconds
FRAMES = FPS * VIDEO_LENGTH


def create_video(input_files: List[Path], out_filename: Path) -> None:
    input_manifest = SCRIPT_DIR / "manifest.txt"
    skip_n = len(input_files) // FRAMES
    with open(input_manifest, "w") as file:
        last_stable_image = None
        print("Analysing images:")
        for path in tqdm(input_files[::skip_n]):
            current_image = cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2GRAY)
            if last_stable_image is None:
                last_stable_image = current_image
                images_passed = 1
            else:
                diff = cv2.absdiff(current_image, last_stable_image)
                diff_sum = diff.sum()
                if diff_sum < 60054292:
                    images_passed += 1
                    continue

            file.write(f"file {path}\n")
            file.write(f"duration {images_passed * FRAME_DURATION}\n")

            images_passed = 1
            last_stable_image = current_image

    ffmpeg = (
        Path().home() / "workspace" / "ffmpeg" / "ffmpeg" if False else "ffmpeg"
    )  # homemade vs conan
    # encoders = ["h264_nvenc", "hevc_nvenc", "libx264", "libx265"]
    for encoder in ["h264_nvenc"]:
        new_out_filename = out_filename.parent / (
            out_filename.stem + f"_{encoder}" + out_filename.suffix
        )
        command = f"{ffmpeg} -f concat -safe 0 -i {input_manifest} -c:v {encoder} -preset slow -b:v 6M -maxrate:v 10M -qmin:v 19 -qmax:v 14 -vf fps={FPS} {new_out_filename}".split()

        subprocess.check_call(command)


time_ranges = []
# abriss altes haus
# time_ranges.append(
#     {
#         "start": datetime(2021, 7, 29, 7, 0),
#         "end": datetime(2021, 7, 29, 17, 0),
#     }
# )
# time_ranges.append(
#     {
#         "start": datetime(2021, 8, 2),
#         "end": datetime(2021, 8, 4),
#     }
# )
time_ranges.append(
    {
        "start": datetime(2021, 10, 1, 10, 0),
        "end": datetime(2021, 11, 2),
    }
)

found_files = find_files(time_ranges)
found_files.sort()

create_video(found_files, SCRIPT_DIR / "oktober.mp4")

print("hello")
