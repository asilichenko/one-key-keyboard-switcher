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

import logging

logger: logging.Logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'right_ctrl_hkl': -0xf57fbde,
    'right_shift_hkl': 0x4090409,
    'key_press_timeout': 0.15,
    'layout_check_interval': 0.5
}


class Config:
    """Reads config from an INI file and stores data into fields."""

    def __init__(self) -> None:
        self.right_ctrl_hkl: int = int(DEFAULT_CONFIG['right_ctrl_hkl'])
        self.right_shift_hkl: int = int(DEFAULT_CONFIG['right_shift_hkl'])
        self.key_press_timeout: float = float(DEFAULT_CONFIG['key_press_timeout'])
        self.layout_check_interval: float = float(DEFAULT_CONFIG['layout_check_interval'])


def main() -> None:
    config: Config = Config()
    print(f'{config.right_ctrl_hkl = }')
    print(f'{config.right_shift_hkl = }')
    print(f'{config.key_press_timeout = }')
    print(f'{config.layout_check_interval = }')


if __name__ == "__main__":
    main()
