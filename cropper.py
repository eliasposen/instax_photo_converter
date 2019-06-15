from pathlib import Path
from tempfile import TemporaryDirectory

import contextlib

with contextlib.redirect_stdout(None):  # Stop pygame welcome message
    import pygame
from pygame.locals import K_LEFT, K_RIGHT, K_UP, K_DOWN, K_RETURN, K_r
from PIL import Image
from typing import Dict, Tuple


class Cropper:
    def __init__(self, img_path: Path, out_img_path: Path, size: Tuple[int, int]):
        # TODO: Load Multiple photos into cropper
        # TODO: Deal with when bounding box is too large for photo(s)
        self.ui_img_len = 500  # TODO: Get size relative to screen in future
        self.out_img_path = out_img_path
        self.crop_width, self.crop_height = size
        self.img_source = Image.open(img_path)
        self.img_resized = self.resize_for_crop()

    def resize_for_crop(self) -> Image:
        width = self.img_source.width
        height = self.img_source.height
        if (
            width <= self.ui_img_len or height <= self.ui_img_len
        ):  # this could cause an issue for "skinny" photos
            self.img_source.save(outpath)
            resized = self.img_source.copy()  # TODO: does this work?
        else:
            if width >= height:
                ratio = height / width
                diff = width - self.ui_img_len
                new_width = self.ui_img_len
                new_height = int(height - (diff * ratio))
            else:
                ratio = width / height
                diff = height - self.ui_img_len
                new_width = int(width - (diff * ratio))
                new_height = self.ui_img_len
            resized = self.img_source.resize((new_width, new_height), Image.ANTIALIAS)
        return resized

    def get_crop_box_percentages(self) -> Tuple:
        width_percent = self.crop_width / self.img_source.width
        height_percent = self.crop_height / self.img_source.height
        return width_percent, height_percent

    def resized_to_source_img_location(self, location):
        if location[0] == 0:
            source_x = 0
        else:
            percentage_across = location[0] / self.img_resized.width
            source_x = self.img_source.width * percentage_across
        if location[1] == 0:
            source_y = 0
        else:
            percentage_down = location[1] / self.img_resized.height
            source_y = self.img_source.height * percentage_down
        return (source_x, source_y)

    def launch(self) -> None:
        pygame.init()
        with TemporaryDirectory() as tmp_dir:
            tmp_img_path = Path(tmp_dir) / "tmp.jpg"
            self.img_resized.save(tmp_img_path)
            top_left = self.get_crop_cooridinates(tmp_img_path)
            self.crop_and_save(top_left)

    def load_surface(self, img_path: Path):
        pygame_img = pygame.image.load(str(img_path.absolute()))
        surface = pygame.display.set_mode(pygame_img.get_rect()[2:])
        surface.blit(pygame_img, (0, 0))
        return surface

    def draw_crop_box(self, surface, size, location):
        crop_box = pygame.Surface(size)
        crop_box.set_alpha(90)
        crop_box.fill((255, 255, 255))
        surface.blit(crop_box, location)

    def is_legal_location(self, location, crop_box_size):
        if (
            location[0] < 0
            or (location[0] + crop_box_size[0]) > self.img_resized.width
            or location[1] < 0
            or (location[1] + crop_box_size[1]) > self.img_resized.height
        ):
            print("illegal")
            return False
        return True

    def get_crop_cooridinates(self, img_path: Path) -> Tuple[float, float]:
        surface = self.load_surface(img_path)
        active_ui = True
        width_percent, height_percent = self.get_crop_box_percentages()
        crop_box_size = (
            self.img_resized.width * width_percent,
            self.img_resized.height * height_percent,
        )
        crop_box_location_x, new_x = 0, 0
        crop_box_location_y, new_y = 0, 0
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
                    self.img_source = self.img_source.transpose(Image.ROTATE_270)
                    self.img_resized = self.img_resized.transpose(Image.ROTATE_270)
                    self.img_resized.save(img_path)

                # Update on change
                if event.type == pygame.KEYDOWN and event.key in update_keys:
                    surface = self.load_surface(img_path)
                    if self.is_legal_location((new_x, new_y), crop_box_size):
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
        return self.resized_to_source_img_location(crop_box_location)

    def crop_and_save(self, top_left: Tuple[int, int]) -> None:
        cropped = self.img_source.crop(
            (
                top_left[0],
                top_left[1],
                top_left[0] + self.crop_width,
                top_left[1] + self.crop_height,
            )
        )
        cropped.save(self.out_img_path)


if "__main__" == __name__:
    c = Cropper(
        Path("test_images/test_crop/crop_me.jpg"),
        Path("test_images/test_crop/cropped.jpg"),
        (1920, 1920),
    )
    c.launch()
