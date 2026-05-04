#  Copyright (C) 2026 Oleksii Sylichenko (a.silichenko@gmail.com)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from pathlib import Path
from PIL import Image

PROJECT_ROOT: Path = Path(__file__).parent.parent
ASSETS_PATH: Path = PROJECT_ROOT / "packaging/msix/Assets"
OUTPUT_PATH: Path = PROJECT_ROOT / "packaging/pyinstaller"

if __name__ == '__main__':
    """
    Конвертує png картинку в ico файл, який містить серію розмірів цієї картинки. 
    Переглянути можна в GIMP.s"""

    input_file: Path = ASSETS_PATH / 'StoreLogo.png'
    output_file: Path = OUTPUT_PATH / 'icon.ico'

    img = Image.open(input_file)

    img.save(
        output_file,
        format="ICO",
        sizes=[
            (16, 16),
            (32, 32),
            (48, 48),
            (64, 64),
            (128, 128),
            (256, 256),
        ]
    )
