import csv
import shutil

from argparse import ArgumentParser, Namespace
from datetime import datetime
from pathlib import Path
from typing import List

from advanced_print import AdvancedPrint


def exit_script(msg: str, code: int = 1):
    AdvancedPrint.red(msg)
    exit(code)

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


def copy_and_rename_photo(file: Path, filename: str, output: Path) -> None:
    destination = output / f"{filename}.JPG"
    shutil.copyfile(file, destination)


def convert(num: int, source: Path, output: Path) -> None:
    if not output.exists():
        AdvancedPrint.underline(output.absolute(), end="")
        print(f" does not exit{'.'*20}", end="")
        output.mkdir()
        AdvancedPrint.blue("CREATED")
    files = list(source.glob("*.jpg"))
    AdvancedPrint.bold(f"\nFound {len(files)} file(s) to convert")
    for idx, file in enumerate(files):
        print(f"\tConverting file {idx+1}/{len(files)}{'.'*20}", end="")
        filename = f"DSCF{num + idx:04d}"
        copy_and_rename_photo(file, filename, output)
        make_csv(filename, output)
        AdvancedPrint.green("DONE")
    print("\nConverted files saved in", end="")
    AdvancedPrint.underline(output.absolute())


def validate_args(args: Namespace) -> str:
    msg = ""
    if args.start_number > 9999:
        msg = "--start_number (-n) can have maximum 4 digits"
    return msg


if "__main__" == __name__:
    argparse = ArgumentParser()
    argparse.add_argument(
        "-n",
        "--start_number",
        required=True,
        type=int,
        help="starting photo number for file names",
    )
    argparse.add_argument(
        "-s", "--source", required=True, help="source folder containing photos"
    )
    argparse.add_argument("-o", "--output", required=True, help="output folder")
    args = argparse.parse_args()

    error_msg = validate_args(args)
    if error_msg:
        exit_script(error_msg)

    convert(args.start_number, Path(args.source), Path(args.output))
