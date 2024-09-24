#  Copyright (C) 2024 Oleksii Sylichenko (a.silichenko@gmail.com)
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

from PIL import Image

FLAG_FILENAME_TEMPLATE: str = 'flags/{}.png'

OUTPUT_FORMAT: str = 'gif'
"""If you use icon in 'png' format (or in 'ico' format but created by pillow lib)
then user's antivirus may recognize your exe file as trojan "Win64:Evo-Gen"""

OUTPUT_FILENAME: str = f'icon.{OUTPUT_FORMAT}'

SIZE: int = 255
SUB_SIZE: int = int(SIZE * 0.75)
SHIFT_POS: int = SIZE - SUB_SIZE


def create_image(country1: str, country2: str) -> Image:
    """Creates an image with two partial overlapping flags."""

    retval: Image = Image.new('RGBA', (SIZE, SIZE))

    image1: Image = Image.open(FLAG_FILENAME_TEMPLATE.format(country1))
    image1 = image1.resize((SUB_SIZE, SUB_SIZE))

    image2: Image = Image.open(FLAG_FILENAME_TEMPLATE.format(country2))
    image2 = image2.resize((SUB_SIZE, SUB_SIZE))

    retval.paste(image1, (0, 0))

    alpha = image2.split()[3]
    retval.paste(image2, (SHIFT_POS, SHIFT_POS), alpha)

    return retval


def generate_icon(country1: str, country2: str, output_filename: str = OUTPUT_FILENAME) -> None:
    """Create image with two partial overlapped flags and saves it as file.

    :param country1: name of the background flag country.
    :param country2: name of the foreground flag country.
    :param output_filename: file name for the output image; default if 'icon.tiff'.
    """

    image: Image = create_image(country1, country2)
    image.save(output_filename, sizes=[image.size])


def copy_icon(input_filename: str, output_filename: str = OUTPUT_FILENAME) -> None:
    """Opens image file and saves it in proper format into proper place.

    :param input_filename: file name of original image.
    :param output_filename: file name of image to save.
    """

    image: Image = Image.open(input_filename)
    image.resize((SIZE, SIZE))
    image.save(output_filename, sizes=[SIZE])


def main() -> None:
    country1 = 'United States'
    country2 = 'Ukraine'
    output_name = 'us-uk'

    output_filename = f'icons/{output_name}.{OUTPUT_FORMAT}'
    generate_icon(country1, country2, output_filename)


if __name__ == "__main__":
    main()
