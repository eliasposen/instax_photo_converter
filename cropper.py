from pathlib import Path
from tempfile import TemporaryDirectory
import pygame
from PIL import Image
from typing import Dict, Tuple


class Cropper:
    def __init__(self, img_path: Path, out_img_path: Path, size: Tuple[int, int]):
        self.img_path = img_path
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
            pygame_img = pygame.image.load(str(tmp_img_path.absolute()))
            surface = pygame.display.set_mode(pygame_img.get_rect()[2:])
            n = True
            while n:
                surface.fill((225, 225, 225))
                surface.blit(pygame_img, (0, 0))
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        n = False
                        break
                    pygame.display.update()
        # coordinates = self.get_crop_cooridinates()
        # self.crop_and_save(coordinates)

    def setup(self):

        n = True
        while n:
            surface.fill((225, 225, 225))
            surface.blit(self.img, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    n = False
                    break
                pygame.display.update()

    def get_crop_cooridinates(self) -> Dict[str, int]:
        return {"left": 0, "top": 0, "right": 100, "bottom": 100}

    def crop_and_save(self, crop_cooridinates: Dict[str, int]) -> None:
        pass


if "__main__" == __name__:
    c = Cropper(
        Path("test_images/test_crop/crop_me.jpg"),
        Path("test_images/test_crop/cropped.jpg"),
        (1000, 1000),
    )
    c.launch()
