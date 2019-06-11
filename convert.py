import csv
import shutil

from argparse import ArgumentParser, Namespace
from datetime import datetime
from pathlib import Path
from typing import List


def default_csv() -> List[List[str]]:
    return [
        ["Effect_information"],
        ["MODEL", "SQ10"],
        ["Firmware_version", "1.00"],
        ["Effect_profile", "1.00"],
        ["Date", datetime.now().strftime("%Y/%m/%d"), ""],
        ["Effect_number", "3", ""],
        ["effect1", "BRIGHTNESS", "+-0"],
        ["effect2", "VIGNETTE", "+-0"],
        ["effect3", "FILTER", "Normal"],
        ["EOF"],
    ]


def make_csv(filename: str, output: Path):
    filepath = output / f"{filename}.CSV"
    rows = default_csv()
    with open(filepath, "w") as csvfile:
        csv_writer = csv.writer(csvfile)
        for row in rows:
            csv_writer.writerow(row)


def copy_and_rename_photo(filename: str, source: Path, output: Path) -> None:
    picture = next(source.glob("*.jpg"))
    destination = output / f"{filename}.JPG"
    shutil.copyfile(picture, destination)


def convert(num: int, source: Path, output: Path, auto_crop: bool) -> None:
    filename = f"DSCF{num:04d}"
    if not output.exists():
        output.mkdir()
    copy_and_rename_photo(filename, source, output)
    make_csv(filename, output)


def validate_args(args: Namespace) -> str:
    msg = ""
    if args.number > 9999:
        msg = "--number can have maximum 4 digits"
    return msg


if "__main__" == __name__:
    argparse = ArgumentParser()
    argparse.add_argument(
        "-n", "--number", required=True, type=int, help="photo number for file names"
    )
    argparse.add_argument(
        "-s", "--source", required=True, help="source folder of photo"
    )
    argparse.add_argument("-o", "--output", required=True, help="output folder")
    argparse.add_argument(
        "-a", "--auto_crop", action="store_true", help="automatically crop input image"
    )
    args = argparse.parse_args()

    error_msg = validate_args(args)
    if error_msg:
        raise TypeError(error_msg)

    convert(args.number, Path(args.source), Path(args.output), args.auto_crop)
