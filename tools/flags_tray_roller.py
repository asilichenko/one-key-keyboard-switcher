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

import threading
from typing import List

import pycountry
from pystray import Icon, Menu, MenuItem

from onekey_layout_switcher.utils.flag_utils import FlagUtils

LAYOUT_COUNTRIES = ['AF', 'AL', 'AM', 'AZ', 'BA', 'BE', 'BG', 'BR', 'BY', 'CA', 'CH', 'CN', 'CS', 'CZ', 'DE', 'DK',
                    'EE', 'ES', 'FI', 'FO', 'FR', 'GB', 'GE', 'GL', 'GR', 'HK', 'HR', 'HU', 'IE', 'IL', 'IN', 'IR',
                    'IS', 'IT', 'JP', 'KG', 'KH', 'KR', 'KZ', 'LA', 'LK', 'LT', 'LU', 'LV', 'MK', 'MN', 'MO', 'MT',
                    'MV', 'MX', 'NG', 'NL', 'NO', 'NP', 'NZ', 'PK', 'PL', 'PT', 'RO', 'RU', 'SA', 'SE', 'SG', 'SI',
                    'SK', 'SN', 'SY', 'TH', 'TJ', 'TM', 'TR', 'TW', 'UA', 'US', 'UZ', 'VN', 'ZA']


class Timer:

    def __init__(self, func, interval: float = 1.0):
        self.stop_event = None
        self._func = func
        self._interval = interval

    def _loop(self):
        while not self.stop_event.wait(self._interval):
            self._func()

    def start_timer(self) -> threading.Event:
        self.stop_event = threading.Event()
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()
        return self.stop_event


class FlagsRoller:
    def __init__(self,
                 flag_utils: FlagUtils,
                 layout_countries: list[str],
                 start_index: int = 0):
        self._tray_icon = Icon(
            name="Flags roller",
            menu=Menu(MenuItem("Exit", self.stop))
        )

        self._flag_utils: FlagUtils = flag_utils

        self._layout_countries: List[str] = layout_countries
        self._index: int = start_index

        self.update_flag()

    def start(self):
        Timer(func=self.next, interval=_interval).start_timer()
        self._tray_icon.run()

    def update_flag(self):
        country_code: str = self._layout_countries[self._index]

        self._tray_icon.icon = self._flag_utils.flag_for(country_code)
        self._tray_icon.title = country_code
        print(self._tray_icon.title)

    def next(self):
        self._index = (self._index + 1) % len(LAYOUT_COUNTRIES)
        self.update_flag()

    def stop(self):
        self._tray_icon.stop()


if __name__ == "__main__":
    _interval = 1.5

    _start_country = (
        # 'CS'
        # 'FO'
        # 'GB'
        # 'US'
        # 'UA'
        # 'CH'
        'NP'
        # 'CA'
        # 'DE'
        # 'FR'
    )

    sprite_file_name = (
        "sprite_64_noline.png"
        # "sprite_72_noline.png"
        # "sprite_16_noline.png"
        # "sprite_24_noline.png"
    )

    _sprite_flags: list[str] = [country.alpha_2 for country in pycountry.countries]

    _flag_utils: FlagUtils = FlagUtils(
        sprite_file_name=sprite_file_name,
        sprite_flags=_sprite_flags
    )

    FlagsRoller(
        flag_utils=_flag_utils,
        layout_countries=LAYOUT_COUNTRIES,
        start_index=LAYOUT_COUNTRIES.index(_start_country)
    ).start()
