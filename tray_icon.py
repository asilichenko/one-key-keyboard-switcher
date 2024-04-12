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
import ctypes
from PIL import Image, ImageDraw, ImageEnhance

"""https://pystray.readthedocs.io/en/latest/usage.html"""
from pystray import Icon, Menu, MenuItem

logger = logging.getLogger(__name__)

LOCALE_SENGLISHCOUNTRYNAME: int = 0x1002
"""Constant to obtain english name of the country/region, for example, Germany for Deutschland.
https://learn.microsoft.com/en-us/windows/win32/intl/locale-senglish-constants"""


def create_image(width, height, color1, color2):
    """Generate an image and draw a pattern."""

    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)

    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)

    return image


UNDEFINED_FLAG = create_image(64, 64, 'red', 'yellow')


class TrayIcon:
    ICON_NAME = "Keyboard layout country flag"

    PAUSE_TEXT = "Pause"
    CONTINUE_TEXT = "Continue"
    EXIT_TEXT = "Exit"

    DIM_LEVEL = 0.5

    def __init__(self, start_listen_keyboard, stop_listen_keyboard, country_id: int):
        self._is_paused = False
        self._pause_item_text = self.PAUSE_TEXT

        self._start_listen_keyboard = start_listen_keyboard
        self._stop_listen_keyboard = stop_listen_keyboard

        self._country_id = country_id
        self._icon = Icon(name=self.ICON_NAME,
                          icon=self._get_flag(),
                          menu=Menu(
                              MenuItem(lambda text: self._pause_item_text, self._toggle_pause),
                              Menu.SEPARATOR,
                              MenuItem(self.EXIT_TEXT, self.stop)
                          ))

    def _get_country_name(self):
        kernel32 = ctypes.windll.kernel32
        country_name = ctypes.create_string_buffer(20)
        result = kernel32.GetLocaleInfoA(self._country_id, LOCALE_SENGLISHCOUNTRYNAME, country_name, len(country_name))
        if result:
            return country_name.value.decode()

    def _get_flag(self):
        retval = None
        try:
            country_name = self._get_country_name()
            if country_name:
                retval = Image.open("flags/" + country_name + ".png")
        except Exception as e:
            logger.error("Flag not found: %s", str(e))
        finally:
            return retval if retval else UNDEFINED_FLAG

    def _dim_icon(self):
        icon = ImageEnhance.Brightness(self._icon.icon).enhance(self.DIM_LEVEL)
        self._icon.icon = ImageEnhance.Color(icon).enhance(self.DIM_LEVEL)

    def _toggle_pause(self):
        self._is_paused = not self._is_paused

        if self._is_paused:
            self._stop_listen_keyboard()
            self._dim_icon()
        else:
            self._start_listen_keyboard()
            self._icon.icon = self._get_flag()

        self._pause_item_text = self.CONTINUE_TEXT if self._is_paused else self.PAUSE_TEXT
        self._icon.update_menu()

    def update_flag(self, country_id):
        self._country_id = country_id
        self._icon.icon = self._get_flag()
        if self._is_paused:
            self._dim_icon()

    def run(self):
        self._start_listen_keyboard()
        self._icon.run()

    def stop(self):
        self._stop_listen_keyboard()
        self._icon.stop()
