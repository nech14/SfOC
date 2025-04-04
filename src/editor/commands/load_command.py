import os.path

from src.editor.commands.base_command import BaseCommand
from src.file import get_name_file, open_gz
from src.file.file import FitsInfoBase, FitsInfo
from src.models.img_data import ImgData


class LoadCommand(BaseCommand):

    def __init__(
            self,
            editor,
            root_path="",
            names_files:list=None,
            start_file=0,
            end_file=None,
            _zip = False,
            fit_format:FitsInfoBase = FitsInfo,
            data_index = None
    ):
        super().__init__(editor)
        self.root_path = root_path
        self.names_files = names_files
        self.start_file = start_file
        self.end_file = end_file
        self._zip = _zip
        self.fit_format = fit_format
        self.data_index = data_index




    def execute(self) -> bool:
        self.saveBackup()



        if self.names_files is None or len(self.names_files) == 0:
            self.names_files = get_name_file(self.root_path)

        if self.end_file is None:
            self.end_file = len(self.names_files)

        for i in range(self.start_file, self.end_file):
            name_path = os.path.join(self.root_path, self.names_files[i])
            print(name_path)

            header, data = open_gz(
                name_path,
                _zip=self._zip,
            )

            img_data = ImgData(
                header,
                data,
                fit_format=self.fit_format,
                data_index=self.data_index
            )

            self._editor.datas.append(img_data)

        return True


