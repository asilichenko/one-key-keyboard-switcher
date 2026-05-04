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

import io
from pathlib import Path

import pycountry
from PIL import Image

from tools import svg_util

PROJECT_ROOT: Path = Path(__file__).parent.parent
FLAGS_LOCATION: Path = PROJECT_ROOT / "build/flags"


def get_flag_image(country_code: str, remove_border: bool, size: int) -> Image.Image:
    svg_path: Path = FLAGS_LOCATION / f'{country_code}.svg'
    if not svg_path.exists():
        raise RuntimeError(f'Missing flag: {code}')

    tree = svg_util.parse(svg_path)

    if country_code == "UA":
        svg_util.fix_ukraine_colors(tree)

    if remove_border:
        svg_util.remove_border_line(tree)

    png_bytes: bytes = svg_util.render(tree, size)

    return Image.open(io.BytesIO(png_bytes))


if __name__ == '__main__':
    FLAG_SIZE: int = 64
    REMOVE_BORDER: bool = True
    OUTPUT_PATH: Path = PROJECT_ROOT / "build"

    country_codes: list[str] = [country.alpha_2 for country in pycountry.countries]
    count: int = len(country_codes)
    print(country_codes)
    print(f'{count = }')
    print()

    sprite_image: Image.Image = Image.new("RGBA", (FLAG_SIZE, count * FLAG_SIZE), (0, 0, 0, 0))

    for i, code in enumerate(country_codes):
        flag_image: Image.Image = get_flag_image(code, REMOVE_BORDER, FLAG_SIZE)
        sprite_image.paste(flag_image, (0, i * FLAG_SIZE))

    sprite_image.show()

    output_file = OUTPUT_PATH / f"sprite_{FLAG_SIZE}_{'noline' if REMOVE_BORDER else 'blackline'}.png"
    print(f'Saving to: {output_file}')

    sprite_image.save(output_file)
