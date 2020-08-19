import csv
import shutil

from argparse import ArgumentParser, Namespace
from datetime import datetime
from pathlib import Path
from typing import List

from cropper import Cropper, CropImage
from style_print import red, blue, green, bold, underline


class InstaxConverter:
    IMAGE_SIZE = (1920, 1920)

    def __init__(self, source: str, output: str, start_number: int):
        self.source_dir = Path(source)
        self.output_dir = Path(output)
        self.check_dirs()

        self.start_number = start_number
        self.crop_images = self.generate_crop_images()

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

    def generate_csvs(self):
        """
        Creates required INSTAX SQ10 csvs for all given images
        """
        for crop_image in self.crop_images:
            filename = crop_image.outpath.name.replace(
                crop_image.outpath.suffix, ".CSV"
            )
            filepath = self.output_dir / filename
            rows = InstaxConverter.default_csv()
            with open(filepath, "w") as csvfile:
                csv_writer = csv.writer(csvfile)
                for row in rows:
                    csv_writer.writerow(row)

    def generate_crop_images(self) -> List[CropImage]:
        crop_images = []
        image_paths = list(self.source_dir.glob("*.jpg"))
        print(bold(f"\nFound {len(image_paths)} file(s) to convert\nLoading..."))
        for idx, image_path in enumerate(image_paths):
            # print("∆", end="")
            filename = f"DSCF{self.start_number + idx:04d}"
            outpath = self.output_dir / f"{filename}.JPG"
            crop_images.append(CropImage(image_path, outpath, square_crop=True))
        return crop_images

    def convert(self) -> None:
        """
        Converts files in source directory into
        format for INSTAX SQ10
        """
        cropper = Cropper(self.crop_images)
        cropper.launch()
        self.generate_csvs()
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
