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
from logging import Logger
import ctypes
from typing import Optional, Callable

from PIL import Image, ImageDraw, ImageEnhance

"""https://pystray.readthedocs.io/en/latest/usage.html"""
from pystray import Icon, Menu, MenuItem

logger: Logger = logging.getLogger(__name__)

LOCALE_SENGLISHCOUNTRYNAME: int = 0x1002
"""Constant to obtain english name of the country/region, for example, Germany for Deutschland.
https://learn.microsoft.com/en-us/windows/win32/intl/locale-senglish-constants"""


def create_image(width: int, height: int, color1: str, color2: str) -> Image:
    """Generate an image and draw a pattern."""

    retval: Image = Image.new('RGB', (width, height), color1)
    dc: ImageDraw = ImageDraw.Draw(retval)

    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)

    return retval


UNDEFINED_FLAG: Image = create_image(64, 64, 'red', 'yellow')


class TrayIcon:
    ICON_NAME: str = "Keyboard layout country flag"

    PAUSE_TEXT: str = "Pause"
    CONTINUE_TEXT: str = "Continue"
    EXIT_TEXT: str = "Exit"

    DIM_LEVEL: float = 0.5

    def __init__(self, start_listen_keyboard: Callable, stop_listen_keyboard: Callable, country_id: int) -> None:
        self._is_paused: bool = False
        self._pause_item_text = self.PAUSE_TEXT

        self._start_listen_keyboard: Callable = start_listen_keyboard
        self._stop_listen_keyboard: Callable = stop_listen_keyboard

        self._country_id: int = country_id
        self._icon: Icon = Icon(name=self.ICON_NAME,
                                icon=self._get_flag(),
                                menu=Menu(
                                    MenuItem(lambda text: self._pause_item_text, self._toggle_pause),
                                    Menu.SEPARATOR,
                                    MenuItem(self.EXIT_TEXT, self.stop)
                                ))

    def _get_country_name(self) -> Optional[str]:
        kernel32 = ctypes.windll.kernel32
        country_name = ctypes.create_string_buffer(20)
        result = kernel32.GetLocaleInfoA(self._country_id, LOCALE_SENGLISHCOUNTRYNAME, country_name, len(country_name))
        return country_name.value.decode() if result else None

    def _get_flag(self) -> Image:
        retval: Optional[Image] = None
        try:
            country_name: Optional[str] = self._get_country_name()
            if country_name:
                retval = Image.open("flags/" + country_name + ".png")
        except Exception as e:
            logger.error(f'Flag not found: {e!s}')
        finally:
            return retval if retval else UNDEFINED_FLAG

    def _dim_icon(self) -> None:
        icon: Image = ImageEnhance.Brightness(self._icon.icon).enhance(self.DIM_LEVEL)
        self._icon.icon = ImageEnhance.Color(icon).enhance(self.DIM_LEVEL)

    def _toggle_pause(self) -> None:
        self._is_paused = not self._is_paused

        if self._is_paused:
            self._stop_listen_keyboard()
            self._dim_icon()
        else:
            self._start_listen_keyboard()
            self._icon.icon = self._get_flag()

        self._pause_item_text: str = self.CONTINUE_TEXT if self._is_paused else self.PAUSE_TEXT
        self._icon.update_menu()

    def update_flag(self, country_id: int) -> None:
        self._country_id = country_id
        self._icon.icon = self._get_flag()
        if self._is_paused:
            self._dim_icon()

    def run(self) -> None:
        self._start_listen_keyboard()
        self._icon.run()

    def stop(self) -> None:
        self._stop_listen_keyboard()
        self._icon.stop()
