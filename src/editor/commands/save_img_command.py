import os.path

import matplotlib.pyplot as plt
from src.editor.commands.base_command import BaseCommand


class SaveImgCommand(BaseCommand):

    def __init__(
            self,
            editor,
            save_folder:str,
            title:str=None,
            file_name:str=None,
            figsize=(1920 / 100, 1080 / 100),
            dpi=100,
            cmap="gray",
            axis="off",
            bbox_inches='tight'
    ):
        super().__init__(editor)
        self.bbox_inches = bbox_inches
        self.dpi = dpi
        self.axis = axis
        self.cmap = cmap
        self.title = title
        self.figsize = figsize
        self.file_name = file_name
        self.save_folder = save_folder



    def execute(self) -> bool:

        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)

        plt.figure(figsize=self.figsize, dpi=self.dpi)
        plt.title(self.title)
        plt.imshow(self._editor.result_img, cmap=self.cmap)
        plt.axis(self.axis)

        if self.file_name is None:
            self.file_name = self._editor.target_img.name

        plt.savefig(self.save_folder + f"/{self.file_name}.png", bbox_inches=self.bbox_inches)
        plt.close()

        return False


