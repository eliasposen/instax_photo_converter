import csv
import shutil
from datetime import datetime
from pathlib import Path
from typing import List

import click

from instax_photo_converter.cropper import Cropper, CropImage
from instax_photo_converter.style_print import (
    red, blue, green, bold, underline
)


class InstaxConverter:
    EXTENSIONS = ("jpg", "jpeg", "JPG", "JPEG")
    IMAGE_SIZE = (1920, 1920)

    def __init__(self, source: str, output: str, start_number: int):
        source_dir = Path(source)
        self.source_images = []
        for ext in self.EXTENSIONS:
            self.source_images.extend(source_dir.glob(f"*.{ext}"))

        self.output_dir = Path(output)

        self.validate()

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

    def validate(self) -> None:
        """
        Verifies given directory exitsts, creates output dir if needed
        """
        if not self.source_images:
            exit_script("No .jpg files found in source directory")

        if not self.output_dir.exists():
            print(
                f"{underline(self.output_dir.absolute())} does not exit{'.'*20}", end=""
            )
            self.output_dir.mkdir()
            print(blue("CREATED"))

    def print_controls(self) -> None:
        print("\n" + underline("Cropping Controls"))
        print(
            "\tMove Crop Box: Arrow Keys\n\tEnlarge Crop "
            "Box: 'h'\n\tShrink Crop Box: 'j'\n\tRotate Image: 'r'\n\tSubmit: "
            "Enter\n\tSkip: Tab"
        )

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
        print(bold(f"\nFound {len(self.source_images)} file(s) to convert\nLoading..."))
        self.print_controls()
        crop_images = []
        for idx, image_path in enumerate(self.source_images):
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
            f"\nConverted picture(s) saved in "
            f"{underline(self.output_dir.absolute())}"
        )


def exit_script(msg: str, code: int = 1):
    print(red(msg))
    exit(code)


@click.command()
@click.option(
    "--source",
    "-s",
    type=click.Path(exists=True, file_okay=False),
    required=True,
    help="Directory containing images to convert",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(file_okay=False),
    required=True,
    help="Directory to save coverted images",
)
@click.option(
    "--start-number",
    "-n",
    type=click.IntRange(0, 9999),
    default=0,
    help="Starting number to use when naming outputted files",
)
def convert(source: str, output: str, start_number: int):
    """
    Convert images to be able to load onto, and print from the Instax SQ10
    digital polaroid camera.
    """
    InstaxConverter(source, output, start_number).convert()

if "__main__" == __name__:
    convert()
