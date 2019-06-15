import csv
import shutil

from argparse import ArgumentParser, Namespace
from datetime import datetime
from pathlib import Path
from typing import List

from cropper import Cropper
from style_print import red, blue, green, bold, underline


class InstaxConverter:
    IMAGE_SIZE = (1920, 1920)

    def __init__(self, source: str, output: str, start_number: int):
        self.source_dir = Path(source)
        self.output_dir = Path(output)
        self.start_number = start_number

    @staticmethod
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

    def check_dirs(self) -> None:
        """
        Verifies given directory exitsts, creates output dir if needed
        """
        if not self.source_dir.exists():
            exit_script("Given source directory does not exist")
        if not self.output_dir.exists():
            print(
                f"{underline(self.output_dir.absolute())} does not exit{'.'*20}", end=""
            )
            self.output_dir.mkdir()
            print(blue("CREATED"))

    def generate_csv(self, filename: str):
        """
        Creates required INSTAX SQ10 csv
        """
        filepath = self.output_dir / f"{filename}.CSV"
        rows = InstaxConverter.default_csv()
        with open(filepath, "w") as csvfile:
            csv_writer = csv.writer(csvfile)
            for row in rows:
                csv_writer.writerow(row)

    def convert(self) -> None:
        """
        Converts files in source directory into
        format for INSTAX SQ10
        """
        self.check_dirs()
        picture_paths = list(self.source_dir.glob("*.jpg"))
        print(bold(f"\nFound {len(picture_paths)} file(s) to convert"))
        for idx, picture_path in enumerate(picture_paths):
            print(f"\tConverting file {idx+1}/{len(picture_paths)}{'.'*20}", end="")

            filename = f"DSCF{self.start_number + idx:04d}"
            destination = self.output_dir / f"{filename}.JPG"
            cropper = Cropper(picture_path, destination, InstaxConverter.IMAGE_SIZE)
            cropper.launch()
            self.generate_csv(filename)

            print(green("DONE"))
        print(
            f"\nConverted picture(s) saved in {underline(self.output_dir.absolute())}"
        )


def exit_script(msg: str, code: int = 1):
    print(red(msg))
    exit(code)


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

    InstaxConverter(args.source, args.output, args.start_number).convert()
