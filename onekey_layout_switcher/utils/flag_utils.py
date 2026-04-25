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

import os.path
from typing import List, Dict, Optional

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFile import ImageFile

import keyboard_layout_controller
import paths
from onekey_layout_switcher.utils import winapi_utils

SPRITE_FLAGS = ['AW', 'AF', 'AO', 'AI', 'AX', 'AL', 'AD', 'AE', 'AR', 'AM', 'AS', 'AQ', 'TF', 'AG', 'AU', 'AT', 'AZ',
                'BI', 'BE', 'BJ', 'BQ', 'BF', 'BD', 'BG', 'BH', 'BS', 'BA', 'BL', 'BY', 'BZ', 'BM', 'BO', 'BR', 'BB',
                'BN', 'BT', 'BV', 'BW', 'CF', 'CA', 'CC', 'CH', 'CL', 'CN', 'CI', 'CM', 'CD', 'CG', 'CK', 'CO', 'KM',
                'CV', 'CR', 'CU', 'CW', 'CX', 'KY', 'CY', 'CZ', 'DE', 'DJ', 'DM', 'DK', 'DO', 'DZ', 'EC', 'EG', 'ER',
                'EH', 'ES', 'EE', 'ET', 'FI', 'FJ', 'FK', 'FR', 'FO', 'FM', 'GA', 'GB', 'GE', 'GG', 'GH', 'GI', 'GN',
                'GP', 'GM', 'GW', 'GQ', 'GR', 'GD', 'GL', 'GT', 'GF', 'GU', 'GY', 'HK', 'HM', 'HN', 'HR', 'HT', 'HU',
                'ID', 'IM', 'IN', 'IO', 'IE', 'IR', 'IQ', 'IS', 'IL', 'IT', 'JM', 'JE', 'JO', 'JP', 'KZ', 'KE', 'KG',
                'KH', 'KI', 'KN', 'KR', 'KW', 'LA', 'LB', 'LR', 'LY', 'LC', 'LI', 'LK', 'LS', 'LT', 'LU', 'LV', 'MO',
                'MF', 'MA', 'MC', 'MD', 'MG', 'MV', 'MX', 'MH', 'MK', 'ML', 'MT', 'MM', 'ME', 'MN', 'MP', 'MZ', 'MR',
                'MS', 'MQ', 'MU', 'MW', 'MY', 'YT', 'NA', 'NC', 'NE', 'NF', 'NG', 'NI', 'NU', 'NL', 'NO', 'NP', 'NR',
                'NZ', 'OM', 'PK', 'PA', 'PN', 'PE', 'PH', 'PW', 'PG', 'PL', 'PR', 'KP', 'PT', 'PY', 'PS', 'PF', 'QA',
                'RE', 'RO', 'RU', 'RW', 'SA', 'SD', 'SN', 'SG', 'GS', 'SH', 'SJ', 'SB', 'SL', 'SV', 'SM', 'SO', 'PM',
                'RS', 'SS', 'ST', 'SR', 'SK', 'SI', 'SE', 'SZ', 'SX', 'SC', 'SY', 'TC', 'TD', 'TG', 'TH', 'TJ', 'TK',
                'TM', 'TL', 'TO', 'TT', 'TN', 'TR', 'TV', 'TW', 'TZ', 'UG', 'UA', 'UM', 'UY', 'US', 'UZ', 'VA', 'VC',
                'VE', 'VG', 'VI', 'VN', 'VU', 'WF', 'WS', 'YE', 'ZA', 'ZM', 'ZW']


class FlagUtils:
    def __init__(self,
                 sprite_file_name: str = "sprite_64_noline.png",
                 sprite_flags=None
                 ):
        self._sprite: ImageFile = self._load_sprite(sprite_file_name)
        self._sprite_flags: List[str] = SPRITE_FLAGS if sprite_flags is None else sprite_flags

        self._cache: Dict[str, Image.Image] = {}

    @staticmethod
    def _load_sprite(file_name: str) -> ImageFile:
        assets_dir: str = paths.get_assets_dir()
        return Image.open(os.path.join(assets_dir, file_name))

    def flag_for(self, country_code: str) -> Image.Image:
        if country_code in self._cache:
            return self._cache[country_code]

        if country_code in self._sprite_flags:
            sprite_index = self._sprite_flags.index(country_code)
            cell_size: int = self._sprite.width
            flag = self._sprite.crop((0, sprite_index * cell_size, cell_size, (sprite_index + 1) * cell_size))
        else:
            flag = self.create_unknown_flag()

        if country_code not in self._cache:
            self._cache[country_code] = flag

        return flag

    def create_unknown_flag(self) -> Image.Image:
        """
        Creates a flag image fitting into a square of given size.
        Background is transparent, flag rectangle is 4:3 centered in the square.
        """
        size = self._sprite.width

        flag_w = size
        flag_h = size * 3 // 4

        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        x0 = 0
        y0 = (size - flag_h) // 2
        x1 = x0 + flag_w - 1
        y1 = y0 + flag_h - 1

        flag_fill = (240, 240, 240, 255)
        draw.rectangle([x0, y0, x1, y1], fill=flag_fill)

        text = "?"
        text_fill = (0, 0, 0, 255)

        font_size = int(flag_h * 0.85)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)

            if font:
                bbox = draw.textbbox((0, 0), text, font=font)
                tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                x = x0 + (flag_w - tw) // 2 - bbox[0]
                y = y0 + (flag_h - th) // 2 - bbox[1]
                draw.text((x, y), text, fill=text_fill, font=font)
        except (IOError, OSError):
            pass

        return img


if __name__ == '__main__':
    _country_id: int = keyboard_layout_controller.get_country_id()
    _country_code: Optional[str] = winapi_utils.get_country_code(_country_id)

    # _country_code = 'aa'
    # _country_code = 'UA'
    # _country_code = 'US'
    # _country_code = 'NP'

    print(f'{_country_code = }')
    if _country_code:
        FlagUtils().flag_for(_country_code).show()
    else:
        FlagUtils().create_unknown_flag().show()
