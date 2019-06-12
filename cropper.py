from pathlib import Path
from tempfile import TemporaryDirectory

import pygame
from pygame.locals import K_LEFT, K_RIGHT
from PIL import Image
from typing import Dict, Tuple


class Cropper:
    def __init__(self, img_path: Path, out_img_path: Path, size: Tuple[int, int]):
        self.out_img_path = out_img_path
        self.size = size
        self.img = Image.open(img_path)

    def resize(self, outpath: Path):
        height = self.img.height
        width = self.img.width
        if width <= self.size[0] or height <= self.size[1]:
            self.img.save(outpath)
            return

        if width >= height:
            ratio = height / width
            diff = width - self.size[0]
            new_width = self.size[0]
            new_height = int(height - (diff * ratio))
        else:
            ratio = width / height
            diff = height - self.size[0]
            new_width = int(width - (diff * ratio))
            new_height = self.size[1]
        self.img = self.img.resize((new_width, new_height))
        self.img.save(outpath)

    def launch(self) -> None:
        pygame.init()
        with TemporaryDirectory() as tmp_dir:
            tmp_img_path = Path(tmp_dir) / "tmp.jpg"
            self.resize(tmp_img_path)
            coordinates = self.get_crop_cooridinates(tmp_img_path)
            self.crop_and_save(coordinates)

    def load_surface(self, img_path: Path) -> Tuple:
        pygame_img = pygame.image.load(str(img_path.absolute()))
        surface = pygame.display.set_mode(pygame_img.get_rect()[2:])
        return surface, pygame_img

    def get_crop_cooridinates(self, img_path: Path) -> Dict[str, int]:
        surface, pygame_img = self.load_surface(img_path)
        active_ui = True
        while active_ui:
            surface.fill((225, 225, 225))
            surface.blit(pygame_img, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == K_LEFT:
                    self.img = self.img.transpose(Image.ROTATE_90)
                    self.img.save(img_path)
                    surface, pygame_img = self.load_surface(img_path)

                if event.type == pygame.KEYDOWN and event.key == K_RIGHT:
                    self.img = self.img.transpose(Image.ROTATE_270)
                    self.img.save(img_path)
                    surface, pygame_img = self.load_surface(img_path)

                if event.type == pygame.QUIT:
                    active_ui = False
                    break
                pygame.display.update()
        pygame.quit()
        return {"left": 0, "top": 0, "right": 100, "bottom": 100}

    def crop_and_save(self, crop_cooridinates: Dict[str, int]) -> None:
        pass


if "__main__" == __name__:
    c = Cropper(
        Path("test_images/test_crop/crop_me.jpg"),
        Path("test_images/test_crop/cropped.jpg"),
        (1920, 1920),
    )
    c.launch()
