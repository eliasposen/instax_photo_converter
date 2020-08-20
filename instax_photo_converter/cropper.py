import contextlib

with contextlib.redirect_stdout(None):  # Stop pygame welcome message
    import pygame

from pathlib import Path
from pygame.locals import (
    K_LEFT,
    K_RIGHT,
    K_UP,
    K_DOWN,
    K_RETURN,
    K_TAB,
    K_e,
    K_j,
    K_r,
    K_w,
    K_h,
)
from PIL import Image
from tempfile import TemporaryDirectory
from typing import Dict, Tuple, List, Union

from instax_photo_converter.style_print import green


class CropImage:
    UI_IMAGE_LEN = 700

    def __init__(
        self,
        img_path: Path,
        outpath: Path,
        crop_size: Tuple[int, int] = None,
        square_crop=False,
    ):
        self.outpath = outpath
        self.image = Image.open(img_path)
        self.ui_image = self.generate_ui_image()
        self.ui_crop_box_location = (0, 0)
        self.square_crop = square_crop
        self.crop_width, self.crop_height = self.validate_crop_size(crop_size)

    def validate_crop_size(self, crop_size: Tuple[int, int]) -> Tuple[int, int]:
        """
        Validates crop_size with image size and square_crop
        """
        if self.square_crop and crop_size:
            raise AttributeError(
                "CropImage can not be given both crop_size and square_crop"
            )
        elif self.square_crop:
            shorter = min(self.image.width, self.image.height)
            crop_size = (shorter, shorter)
        elif not crop_size:
            crop_size = (self.image.width, self.image.height)
        else:
            if crop_size[0] <= 0 or crop_size[1] <= 0:
                raise AttributeError("crop_size values must be integers greater than 0")
            width = (
                crop_size[0] if crop_size[0] <= self.image.width else self.image.width
            )
            height = (
                crop_size[1] if crop_size[1] <= self.image.height else self.image.height
            )
            crop_size = (width, height)
        return crop_size

    def transpose(self, rotation) -> None:
        self.image = self.image.transpose(rotation)
        self.ui_image = self.ui_image.transpose(rotation)
        self.resize_ui_crop_box(0, 0)

    def move_ui_crop_box(self, delta_x: int, delta_y: int) -> None:
        new_location = [
            self.ui_crop_box_location[0] + delta_x,
            self.ui_crop_box_location[1] + delta_y,
        ]
        ui_crop_box = self.get_ui_crop_box_size()
        if new_location[0] < 0:
            new_location[0] = 0
        elif new_location[0] + ui_crop_box[0] > self.ui_image.width:
            new_location[0] = self.ui_image.width - ui_crop_box[0]
        if new_location[1] < 0:
            new_location[1] = 0
        elif new_location[1] + ui_crop_box[1] > self.ui_image.height:
            new_location[1] = self.ui_image.height - ui_crop_box[1]

        self.ui_crop_box_location = (new_location[0], new_location[1])

    def resize_ui_crop_box(self, delta_w: int, delta_h: int) -> None:
        if self.square_crop:
            if delta_w < 0 or delta_h < 0:
                delta = min(delta_w, delta_h)
            else:
                delta = max(delta_w, delta_h)
            delta_w, delta_h = delta, delta

        new_width = self.crop_width + delta_w
        new_height = self.crop_height + delta_h

        if new_width < 0:
            new_width = 1
        elif new_width > self.image.width:
            new_width = self.image.width
        if new_height < 0:
            new_height = 1
        elif new_height > self.image.height:
            new_height = self.image.height

        if self.square_crop and new_height != new_width:
            return

        self.crop_width = new_width
        self.crop_height = new_height
        self.move_ui_crop_box(0, 0)

    def get_ui_crop_box_size(self) -> Tuple[int, int]:
        width_percent = self.crop_width / self.image.width
        height_percent = self.crop_height / self.image.height
        return (
            self.ui_image.width * width_percent,
            self.ui_image.height * height_percent,
        )

    def generate_ui_image(self) -> Image:
        width = self.image.width
        height = self.image.height
        if (
            width <= CropImage.UI_IMAGE_LEN or height <= CropImage.UI_IMAGE_LEN
        ):  # this could cause an issue for "skinny" photos
            ui_image = self.image.copy()  # TODO: does this work?
        else:
            if width >= height:
                ratio = height / width
                diff = width - CropImage.UI_IMAGE_LEN
                new_width = CropImage.UI_IMAGE_LEN
                new_height = int(height - (diff * ratio))
            else:
                ratio = width / height
                diff = height - CropImage.UI_IMAGE_LEN
                new_width = int(width - (diff * ratio))
                new_height = CropImage.UI_IMAGE_LEN
            ui_image = self.image.resize((new_width, new_height), Image.ANTIALIAS)
        return ui_image

    def convert_ui_crop_box_location(self) -> Tuple[int, int]:
        if self.ui_crop_box_location[0] == 0:
            source_x = 0
        else:
            percentage_across = self.ui_crop_box_location[0] / self.ui_image.width
            source_x = self.image.width * percentage_across
        if self.ui_crop_box_location[1] == 0:
            source_y = 0
        else:
            percentage_down = self.ui_crop_box_location[1] / self.ui_image.height
            source_y = self.image.height * percentage_down
        return (source_x, source_y)

    def crop_and_save(self) -> None:
        top_left = self.convert_ui_crop_box_location()
        cropped = self.image.crop(
            (
                top_left[0],
                top_left[1],
                top_left[0] + self.crop_width,
                top_left[1] + self.crop_height,
            )
        )
        cropped.save(self.outpath)


class Cropper:
    def __init__(
        self,
        crop_images: Union[CropImage, List[CropImage]],
        move_delta: int = 3,
        resize_delta: int = 20,
    ):
        if type(crop_images) != list:
            crop_images = [crop_images]
        self.crop_images = crop_images
        self.move_delta = move_delta
        self.resize_delta = resize_delta

    def launch(self) -> None:
        pygame.init()
        with TemporaryDirectory() as tmp_dir:
            tmp_img_path = Path(tmp_dir) / "cropper_ui_image.jpg"
            for idx, crop_image in enumerate(self.crop_images):
                print(f"\tCropping image {idx+1}/{len(self.crop_images)}", end="")
                crop_image.ui_image.save(tmp_img_path)
                self.place_crop_box(crop_image, tmp_img_path)
                crop_image.crop_and_save()
                print(f"{'.'*20}{green('DONE')}")

    def load_surface(self, img_path: Path):
        pygame_img = pygame.image.load(str(img_path.absolute()))
        surface = pygame.display.set_mode(pygame_img.get_rect()[2:])
        surface.blit(pygame_img, (0, 0))
        return surface

    def draw_crop_box(
        self, surface, size: Tuple[int, int], location: Tuple[int, int] = (0, 0)
    ):
        # w, h
        top_bar = {"loc": (0, 0), "size": (surface.get_width(), location[1])}
        bottom_bar = {
            "loc": (0, location[1] + size[1]),
            "size": (
                surface.get_width(),
                surface.get_height() - (location[1] + size[1]) + 1,
            ),
        }
        left_bar = {"loc": (0, 0), "size": (location[0], surface.get_height())}
        right_bar = {
            "loc": (location[0] + size[0], 0),
            "size": (
                surface.get_width() - (location[0] + size[0]) + 1,
                surface.get_height(),
            ),
        }

        for bar in [top_bar, bottom_bar, left_bar, right_bar]:
            box = pygame.Surface(bar["size"])
            box.fill((0, 0, 0))
            surface.blit(box, bar["loc"])

        # crop_box = pygame.Surface(size)
        # crop_box.set_alpha(90)
        # crop_box.fill((255, 255, 255))
        # surface.blit(crop_box, location)

    def place_crop_box(
        self, crop_image: CropImage, tmp_path: Path
    ) -> Tuple[float, float]:
        # Setup
        surface = self.load_surface(tmp_path)
        crop_box_size = crop_image.get_ui_crop_box_size()
        self.draw_crop_box(surface, crop_box_size)

        cropping = True
        update_keys = [K_LEFT, K_RIGHT, K_UP, K_DOWN, K_r, K_w, K_h, K_e, K_j]
        while cropping:
            for event in pygame.event.get():
                # Move crop_box
                if event.type == pygame.KEYDOWN and event.key == K_LEFT:
                    crop_image.move_ui_crop_box(-self.move_delta, 0)
                if event.type == pygame.KEYDOWN and event.key == K_RIGHT:
                    crop_image.move_ui_crop_box(self.move_delta, 0)
                if event.type == pygame.KEYDOWN and event.key == K_UP:
                    crop_image.move_ui_crop_box(0, -self.move_delta)
                if event.type == pygame.KEYDOWN and event.key == K_DOWN:
                    crop_image.move_ui_crop_box(0, self.move_delta)

                # Resize crop_box
                if event.type == pygame.KEYDOWN and event.key == K_w:
                    crop_image.resize_ui_crop_box(self.resize_delta, 0)
                if event.type == pygame.KEYDOWN and event.key == K_e:
                    crop_image.resize_ui_crop_box(-self.resize_delta, 0)
                if event.type == pygame.KEYDOWN and event.key == K_h:
                    crop_image.resize_ui_crop_box(0, self.resize_delta)
                if event.type == pygame.KEYDOWN and event.key == K_j:
                    crop_image.resize_ui_crop_box(0, -self.resize_delta)

                # Rotate image
                if event.type == pygame.KEYDOWN and event.key == K_r:
                    crop_image.transpose(Image.ROTATE_270)
                    crop_image.ui_image.save(tmp_path)

                # Update on change
                if event.type == pygame.KEYDOWN and event.key in update_keys:
                    surface = self.load_surface(tmp_path)
                    crop_box_size = crop_image.get_ui_crop_box_size()
                    self.draw_crop_box(
                        surface, crop_box_size, crop_image.ui_crop_box_location
                    )

                # Skip
                if event.type == pygame.KEYDOWN and event.key == K_TAB:
                    pygame.quit()
                    return
                # Finish cropping
                if (
                    event.type == pygame.QUIT
                    or event.type == pygame.KEYDOWN
                    and event.key == K_RETURN
                ):
                    cropping = False
                    break

                pygame.display.update()
        pygame.quit()


if "__main__" == __name__:
    img = CropImage(
        Path("test_images/test_crop/crop_me.jpg"),
        Path("test_images/test_crop/cropped.jpg"),
        # crop_size=(100000000, 1000000)
        square_crop=True,
    )
    c = Cropper(img)
    c.launch()
