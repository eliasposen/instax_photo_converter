from pathlib import Path
from tempfile import TemporaryDirectory

import contextlib

with contextlib.redirect_stdout(None):  # Stop pygame welcome message
    import pygame
from pygame.locals import K_LEFT, K_RIGHT, K_UP, K_DOWN, K_RETURN, K_r
from PIL import Image
from typing import Dict, Tuple, List, Union


class CropImage:
    def __init__(self, img_path: Path, outpath: Path, crop_size: Tuple[int, int]):
        # TODO: Deal with when bounding box is too large for photo(s)
        self.ui_image_length = 500  # TODO: Get size relative to screen in future

        self.outpath = outpath
        self.crop_width, self.crop_height = crop_size
        self.image = Image.open(img_path)
        self.ui_image = self.genertate_ui_image()

    def transpose(self, rotation) -> None:
        self.image = self.image.transpose(rotation)
        self.ui_image = self.ui_image.transpose(rotation)

    def is_legal_crop_box(self, location: Tuple[int, int]) -> bool:
        ui_crop_box = self.get_ui_crop_box_size()
        if (
            location[0] < 0
            or (location[0] + ui_crop_box[0]) > self.ui_image.width
            or location[1] < 0
            or (location[1] + ui_crop_box[1]) > self.ui_image.height
        ):
            return False
        return True

    def get_ui_crop_box_size(self) -> Tuple[int, int]:
        width_percent = self.crop_width / self.image.width
        height_percent = self.crop_height / self.image.height
        return (
            self.ui_image.width * width_percent,
            self.ui_image.height * height_percent,
        )

    def genertate_ui_image(self) -> Image:
        width = self.image.width
        height = self.image.height
        if (
            width <= self.ui_image_length or height <= self.ui_image_length
        ):  # this could cause an issue for "skinny" photos
            self.image.save(outpath)
            ui_image = self.image.copy()  # TODO: does this work?
        else:
            if width >= height:
                ratio = height / width
                diff = width - self.ui_image_length
                new_width = self.ui_image_length
                new_height = int(height - (diff * ratio))
            else:
                ratio = width / height
                diff = height - self.ui_image_length
                new_width = int(width - (diff * ratio))
                new_height = self.ui_image_length
            ui_image = self.image.resize((new_width, new_height), Image.ANTIALIAS)
        return ui_image

    def ui_to_source_location(self, location: Tuple[int, int]) -> Tuple[int, int]:
        if location[0] == 0:
            source_x = 0
        else:
            percentage_across = location[0] / self.ui_image.width
            source_x = self.image.width * percentage_across
        if location[1] == 0:
            source_y = 0
        else:
            percentage_down = location[1] / self.ui_image.height
            source_y = self.image.height * percentage_down
        return (source_x, source_y)

    def crop_and_save(self, top_left: Tuple[int, int]) -> None:
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
    def __init__(self, crop_images: Union[CropImage, List[CropImage]]):
        # TODO: Load Multiple photos into cropper
        if type(crop_images) != list:
            crop_images = [crop_images]
        self.crop_images = crop_images

    def launch(self) -> None:
        pygame.init()
        with TemporaryDirectory() as tmp_dir:
            tmp_img_path = Path(tmp_dir) / "tmp.jpg"
            for crop_image in self.crop_images:
                crop_image.ui_image.save(tmp_img_path)
                top_left_location = self.get_crop_location(crop_image, tmp_img_path)
                crop_image.crop_and_save(top_left_location)

    def load_surface(self, img_path: Path):
        pygame_img = pygame.image.load(str(img_path.absolute()))
        surface = pygame.display.set_mode(pygame_img.get_rect()[2:])
        surface.blit(pygame_img, (0, 0))
        return surface

    def draw_crop_box(
        self, surface, size: Tuple[int, int], location: Tuple[int, int] = (0, 0)
    ):
        crop_box = pygame.Surface(size)
        crop_box.set_alpha(90)
        crop_box.fill((255, 255, 255))
        surface.blit(crop_box, location)

    def get_crop_location(
        self, crop_image: CropImage, tmp_path: Path
    ) -> Tuple[float, float]:
        surface = self.load_surface(tmp_path)

        crop_box_size = crop_image.get_ui_crop_box_size()
        crop_box_location_x, new_x = 0, 0
        crop_box_location_y, new_y = 0, 0
        self.draw_crop_box(surface, crop_box_size)

        active_ui = True
        delta = 2
        update_keys = [K_LEFT, K_RIGHT, K_UP, K_DOWN, K_r]
        while active_ui:
            for event in pygame.event.get():
                # Move crop_box
                if event.type == pygame.KEYDOWN and event.key == K_LEFT:
                    new_x = crop_box_location_x - delta
                if event.type == pygame.KEYDOWN and event.key == K_RIGHT:
                    new_x = crop_box_location_x + delta
                if event.type == pygame.KEYDOWN and event.key == K_UP:
                    new_y = crop_box_location_y - delta
                if event.type == pygame.KEYDOWN and event.key == K_DOWN:
                    new_y = crop_box_location_y + delta

                # Rotate crop_box
                if event.type == pygame.KEYDOWN and event.key == K_r:
                    crop_image.transpose(Image.ROTATE_270)
                    crop_image.ui_image.save(tmp_path)

                # Update on change
                if event.type == pygame.KEYDOWN and event.key in update_keys:
                    surface = self.load_surface(tmp_path)
                    if crop_image.is_legal_crop_box((new_x, new_y)):
                        crop_box_location_x, crop_box_location_y = new_x, new_y
                    else:
                        new_x, new_y = crop_box_location_x, crop_box_location_y
                    crop_box_location = (crop_box_location_x, crop_box_location_y)
                    self.draw_crop_box(surface, crop_box_size, crop_box_location)

                if (
                    event.type == pygame.QUIT
                    or event.type == pygame.KEYDOWN
                    and event.key == K_RETURN
                ):
                    active_ui = False
                    break

                pygame.display.update()
        pygame.quit()
        return crop_image.ui_to_source_location(crop_box_location)


if "__main__" == __name__:
    img = CropImage(
        Path("test_images/test_crop/crop_me.jpg"),
        Path("test_images/test_crop/cropped.jpg"),
        (1920, 1920),
    )
    c = Cropper(img)
    c.launch()
