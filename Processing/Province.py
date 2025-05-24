import os
from pathlib import Path
from typing import List

from Processing.GeoObject import GeoObject


class Province:
        path: str
        files: List[str]
        objects: List[object]

        def __init__(self, path):
                self.path = path

        def find_files(self):
                directory = Path(self.path)
                self.files = [file.name for file in directory.iterdir() if file.suffix == '.shp']

        def process_files(self):
                for file in self.files:
                        geo = GeoObject(file)